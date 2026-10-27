#!/usr/bin/env python3
"""diagram-driven 图表审计脚本（跨平台：Windows / macOS / Linux）。

替代原 AUDIT.md 中的 bash 片段（grep -oP / date -d / /tmp 在 Windows 不可用）。
依赖：仅 Python 3.9+ 标准库；git 可选（用于时效审计，缺失时回退文件 mtime）。

用法：
    python audit_diagrams.py --root ai/diagrams
    python audit_diagrams.py --root ai/diagrams --check naming,placement --strict
    python audit_diagrams.py --root ai/diagrams --stack kotlin --output report.md
    python audit_diagrams.py --root ai/diagrams --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

# ---------------------------------------------------------------- 常量

# 前缀 -> 允许存放的目录。feature- 允许 refactoring/（重构对比图沿用 feature- 前缀）
PREFIX_DIRS = {
    "feature": {"features", "refactoring"},
    "flow": {"features", "journeys"},
    "sequence": {"journeys"},
    "lane": {"journeys", "features"},
    "arch": {"architecture"},
    "er": {"architecture"},
    "test": {"tests"},
}
VALID_PREFIX_RE = re.compile(r"^(feature|sequence|arch|flow|lane|er|test)-[a-z0-9-]+\.md$")

TYPES = "Feature|Sequence|Architecture|Flow|Swimlane|ER|Test"
REQUIRED_SECTIONS = ["## Purpose", "## Diagram", "## Key Insights", "## Change History"]
REQUIRED_META = ["**Type:**", "**Last Updated:**", "**Related Files:**"]
IMPACT_SYMBOLS = "⚡💾🛡️✅⏱️🔄📊🎯"

# 错误路径：必须同时出现「故障信号」与「恢复出口」
ERROR_SIGNAL = ["错误", "异常", "失败", "超时", "error", "fail", "timeout", "exception"]
RECOVERY_SIGNAL = ["重试", "恢复", "兜底", "降级", "重连", "retry", "fallback", "recover", "recover"]

ALL_CHECKS = ["naming", "placement", "structure", "ddd", "freshness", "index", "coverage"]

# ---------------------------------------------------------------- 工具


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def git_last_commit_ts(rel_path: str, cwd: Path) -> int | None:
    """返回文件最后一次提交的 unix 秒；非 git 仓库或无提交返回 None。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel_path],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    s = (out.stdout or "").strip()
    return int(s) if s.isdigit() else None


def camel_to_kebab(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).lower().strip("-")


def find_diagrams(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        p for p in root.rglob("*.md") if p.name.lower() != "readme.md"
    )


def detect_stack(project: Path, forced: str) -> str:
    if forced != "auto":
        return forced
    if (project / "src" / "main" / "kotlin").is_dir() or (project / "build.gradle.kts").exists():
        return "kotlin"
    if (project / "package.json").exists() or (project / "src" / "features").is_dir():
        return "frontend"
    return "unknown"


def scan_modules(project: Path, stack: str) -> list[tuple[str, str]]:
    """返回 [(模块名, 相对路径)]，覆盖 Kotlin 与前端两种主栈。"""
    found: list[tuple[str, str]] = []
    if stack == "kotlin":
        base = project / "src" / "main" / "kotlin"
        if not base.is_dir():
            base = project / "src"
        for p in base.rglob("*.kt"):
            stem = p.stem
            if not stem.endswith(("Controller", "Service", "Repository")):
                continue
            mod = re.sub(r"(Controller|Service|Repository)$", "", stem)
            if mod:
                found.append((camel_to_kebab(mod), str(p.relative_to(project)).replace("\\", "/")))
    elif stack == "frontend":
        feats = project / "src" / "features"
        if feats.is_dir():
            for d in sorted(feats.iterdir()):
                if d.is_dir():
                    found.append((camel_to_kebab(d.name), str(d.relative_to(project)).replace("\\", "/")))
        for p in list((project / "src" / "components").rglob("*Page.tsx")) + list(
            (project / "src" / "components").rglob("*View.tsx")
        ):
            found.append((camel_to_kebab(p.stem), str(p.relative_to(project)).replace("\\", "/")))
    # 去重保序
    seen, out = set(), []
    for name, path in found:
        if name and name not in seen:
            seen.add(name)
            out.append((name, path))
    return out


# ---------------------------------------------------------------- 检查项


def check_naming_placement(files: list[Path], root: Path) -> tuple[list[dict], list[dict]]:
    naming, placement = [], []
    for f in files:
        rel = f.relative_to(root)
        if not VALID_PREFIX_RE.match(f.name):
            naming.append(
                {
                    "file": str(rel).replace("\\", "/"),
                    "issue": "文件名不符合 `{prefix}-{name}.md` 规范",
                    "fix": "改为 feature-/sequence-/arch-/flow-/lane-/er-/test- 前缀 + 小写连字符",
                }
            )
        prefix = f.name.split("-", 1)[0]
        allowed = PREFIX_DIRS.get(prefix)
        top = rel.parts[0] if len(rel.parts) > 1 else ""
        if allowed and top not in allowed:
            placement.append(
                {
                    "file": str(rel).replace("\\", "/"),
                    "issue": f"`{prefix}-` 前缀应存放于 {'/'.join(sorted(allowed))}，当前在 {top or '根目录'}",
                    "fix": f"移动至 {'/'.join(sorted(allowed))}/",
                }
            )
    return naming, placement


def check_structure_ddd(files: list[Path], root: Path) -> tuple[list[dict], list[dict]]:
    structure, ddd = [], []
    for f in files:
        rel = str(f.relative_to(root)).replace("\\", "/")
        text = read_text(f)

        missing = [s for s in REQUIRED_SECTIONS if s not in text]
        missing += [m for m in REQUIRED_META if m not in text]
        if missing:
            structure.append({"file": rel, "issue": "缺失必填项: " + "、".join(missing), "fix": "按标准模板补齐"})

        problems = []
        if "Front-Stage" not in text and "前台" not in text:
            problems.append("未划分前台 (Front-Stage)")
        if "Back-Stage" not in text and "后台" not in text:
            problems.append("未划分后台 (Back-Stage)")
        if not any(c in text for c in IMPACT_SYMBOLS):
            problems.append("无任何用户价值影响标注")
        low = text.lower()
        if not any(s in low for s in ERROR_SIGNAL):
            problems.append("缺少错误/异常分支")
        elif not any(s in low for s in RECOVERY_SIGNAL):
            problems.append("错误分支缺少用户恢复出口")
        if problems:
            ddd.append({"file": rel, "issue": "；".join(problems), "fix": "回到双舞台视角重构，补标注与自愈路径"})
    return structure, ddd


def check_freshness(files: list[Path], root: Path, project: Path, stale_days: int) -> list[dict]:
    issues = []
    today = datetime.now(timezone.utc).date()
    for f in files:
        rel = str(f.relative_to(root)).replace("\\", "/")
        text = read_text(f)
        m = re.search(r"\*\*Last Updated:\*\*\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
        if not m:
            issues.append({"file": rel, "issue": "未标注 Last Updated", "fix": "补齐日期"})
            continue
        try:
            updated = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            issues.append({"file": rel, "issue": f"Last Updated 格式非法: {m.group(1)}", "fix": "改为 YYYY-MM-DD"})
            continue

        age = (today - updated).days
        if age > stale_days:
            issues.append({"file": rel, "issue": f"已 {age} 天未更新（阈值 {stale_days} 天）", "fix": "复核代码是否仍与图一致"})
            continue

        # 关联代码的最后提交是否晚于图表日期
        block = re.search(r"\*\*Related Files:\*\*(.*?)(?:\n##|\Z)", text, re.S)
        if not block:
            continue
        newest = None
        newest_file = ""
        for line in block.group(1).splitlines():
            p = line.strip().strip("-* ").strip("` ")
            if not p or p.startswith("#"):
                continue
            ts = git_last_commit_ts(p, project)
            if ts and (newest is None or ts > newest):
                newest, newest_file = ts, p
        if newest and datetime.fromtimestamp(newest, timezone.utc).date() > updated:
            code_date = datetime.fromtimestamp(newest, timezone.utc).date()
            issues.append(
                {
                    "file": rel,
                    "issue": f"关联代码 {newest_file} 于 {code_date} 变更，晚于图表 {updated}",
                    "fix": "同步刷新图与 Change History",
                }
            )
    return issues


def check_index(root: Path, files: list[Path]) -> tuple[list[dict], list[dict]]:
    readme = root / "README.md"
    dead, missing = [], []
    if not readme.exists():
        return [{"file": "README.md", "issue": "总索引缺失", "fix": "创建 README.md 索引"}], [
            {"file": str(f.relative_to(root)).replace("\\", "/"), "issue": "无索引可收录", "fix": "创建 README.md"}
            for f in files
        ]

    text = read_text(readme)
    links = re.findall(r"\]\(([^)]+)\)", text)
    for link in links:
        if link.startswith(("http://", "https://", "#")):
            continue
        target = (root / link.split("#")[0]).resolve()
        if not target.exists():
            dead.append({"file": link, "issue": "索引指向的物理文件不存在", "fix": "修复或删除该条目"})

    indexed = {l.split("#")[0].replace("\\", "/").lstrip("./") for l in links}
    for f in files:
        rel = str(f.relative_to(root)).replace("\\", "/")
        if rel not in indexed and f.name not in indexed:
            missing.append({"file": rel, "issue": "图表未登记至 README 索引", "fix": "追加索引条目"})
    return dead, missing


def check_coverage(root: Path, files: list[Path], project: Path, stack: str) -> tuple[str, list[dict]]:
    modules = scan_modules(project, stack)
    if not modules:
        return stack, []
    corpus = "\n".join(read_text(f) for f in files).lower()
    gaps = []
    for name, path in modules:
        if name not in corpus and name.replace("-", "") not in corpus.replace("-", ""):
            gaps.append({"file": name, "issue": f"核心模块 `{path}` 无对应图表", "fix": "创建 feature-/sequence- 图"})
    return stack, gaps


# ---------------------------------------------------------------- 报告


def render(result: dict) -> str:
    out = [
        "# 图表审计报告 (Diagram Audit Report)",
        "",
        f"**审计日期:** {result['date']}  ",
        f"**图表总数:** {result['total']}  ",
        f"**技术栈识别:** {result['stack']}",
        "",
        "## 问题总览",
        "",
        f"- 高优先级（结构/DDD 合规缺失）: {len(result['high'])}",
        f"- 中优先级（命名、归档、时效、索引、覆盖）: {len(result['mid'])}",
        f"- 低优先级（未收录索引等）: {len(result['low'])}",
        "",
    ]

    def block(title: str, items: list[dict], empty: str) -> None:
        out.append(f"## {title}")
        out.append("")
        if not items:
            out.append(f"{empty}")
            out.append("")
            return
        for n, item in enumerate(items, 1):
            out.append(f"{n}. `{item['file']}` — {item['issue']}")
            out.append(f"   - 整改: {item['fix']}")
        out.append("")

    block("高优先级：结构与 DDD 合规", result["high"], "无")
    block("中优先级：命名、归档、时效、索引、覆盖率", result["mid"], "无")
    block("低优先级：索引收录", result["low"], "无")
    return "\n".join(out)


# ---------------------------------------------------------------- 主流程


def main() -> int:
    ap = argparse.ArgumentParser(description="D3 图表审计（跨平台）")
    ap.add_argument("--root", default="ai/diagrams", help="图表根目录")
    ap.add_argument("--project", default=".", help="项目根目录（覆盖率/时效审计用）")
    ap.add_argument(
        "--check",
        default="all",
        help="逗号分隔的检查项: " + ",".join(ALL_CHECKS) + "，或 all",
    )
    ap.add_argument("--stack", default="auto", choices=["auto", "kotlin", "frontend", "unknown"])
    ap.add_argument("--stale-days", type=int, default=90, help="陈旧阈值（天），默认 90")
    ap.add_argument("--output", help="报告写入文件（默认打印到 stdout）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="存在高优先级问题时返回退出码 1")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    project = Path(args.project).resolve()
    checks = ALL_CHECKS if args.check.strip() == "all" else [c.strip() for c in args.check.split(",")]

    files = find_diagrams(root)
    if not files:
        msg = f"未在 {root} 找到任何图表文件（README.md 已排除）。"
        print(msg)
        return 0 if not args.strict else 1

    stack = detect_stack(project, args.stack)
    naming = placement = structure = ddd = freshness = dead = missing = coverage = []
    if "naming" in checks or "placement" in checks:
        naming, placement = check_naming_placement(files, root)
    if "structure" in checks or "ddd" in checks:
        structure, ddd = check_structure_ddd(files, root)
    if "freshness" in checks:
        freshness = check_freshness(files, root, project, args.stale_days)
    if "index" in checks:
        dead, missing = check_index(root, files)
    if "coverage" in checks:
        stack, coverage = check_coverage(root, files, project, stack)

    high = ddd + structure
    mid = naming + placement + freshness + dead + coverage
    result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "root": str(root),
        "total": len(files),
        "stack": stack,
        "high": high,
        "mid": mid,
        "low": missing,
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"报告已写入: {args.output}")
    else:
        print(payload)

    return 1 if (args.strict and high) else 0


if __name__ == "__main__":
    sys.exit(main())
