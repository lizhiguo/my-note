#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
okf_lint.py — OKF v0.2 + LLM-Wiki 知识库体检

用法:
    python okf_lint.py <bundle_root>            # 报告
    python okf_lint.py <bundle_root> --json     # 机器可读
    python okf_lint.py <bundle_root> --strict   # 有 P0 时退出码 1

设计原则:
    - 确定性检查，不做语义判断，不调用 LLM
    - 只报告不修改。修复由 agent 或用户决定
    - 容忍未知 type 与未知 frontmatter 键（OKF §11 强制要求）
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------- 配置

RESERVED = {"index.md", "log.md"}

# 本 bundle 的 schema/入口文件：不是概念页，免 frontmatter 校验。
# （LLM-Wiki 规定 wiki/ 根目录只放 schema 文件）
SCHEMA_FILES = {"wiki/索引.md", "wiki/操作日志.md", "wiki/知识库使用指南.md"}


# 本 bundle 约定的 type 词表（OKF 不注册 type，这里只查拼写漂移）
KNOWN_TYPES = {
    "Concept", "Hub", "Source Digest", "Project", "Tech Design",
    "ADR", "Person", "Schema", "Playbook", "Attested Computation",
    "Reference", "Metric", "API Endpoint",
}

VALID_STATUS = {"draft", "stable", "deprecated"}

# OKF v0.1 已废弃字段
LEGACY_KEYS = {"timestamp"}

ACTOR_RE = re.compile(r"^(human:[^/\s]+|[^/\s]+/[^/\s]+|process:[^/\s]+)$")

# ---------------------------------------------------------------- 路径解析

CONFIG_NAME = ".agent-wiki.json"


def resolve_bundle_root(explicit=None, start=None):
    """按 SKILL.md §0 的优先级解析 bundle_root。

    1. 显式传入的参数
    2. start（或 cwd）若本身是 bundle（含 wiki/索引.md）
    3. ~/.agent-wiki.json 的 wikiRoot
    返回 (root, source)；解析不出返回 (None, None)。
    """
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit)), "argument"

    def is_bundle(p):
        return bool(p) and os.path.isfile(os.path.join(p, "wiki", "索引.md"))

    probe = start or os.getcwd()
    probe = os.path.abspath(probe)
    for cand in (probe, os.path.dirname(probe)):
        if is_bundle(cand):
            return cand, "cwd"

    cfg = os.path.join(os.path.expanduser("~"), CONFIG_NAME)
    if os.path.isfile(cfg):
        try:
            with open(cfg, encoding="utf-8") as fh:
                data = json.load(fh)
            root = data.get("wikiRoot")
            if root:
                return os.path.abspath(os.path.expanduser(root)), "config"
        except (OSError, ValueError) as exc:
            print("解析 %s 失败: %s" % (cfg, exc), file=sys.stderr)

    return None, None
ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?"
    r"(Z|[+-]\d{2}:?\d{2})$"
)
FOOTNOTE_REF = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF = re.compile(r"^\[\^([^\]]+)\]:", re.M)
WIKILINK = re.compile(r"\[\[([^\]|#]+)")
MDLINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# 附件扩展名：Obsidian 的 ![[image.png]] / [[image.png]] 属于嵌入，
# 目标不在 bundle 的 .md 集合里，不按断链报。
ATTACH_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp",
              ".pdf", ".mp3", ".mp4", ".mov", ".webm", ".ogg", ".wav",
              ".xlsx", ".docx", ".pptx", ".csv", ".zip", ".canvas"}


# ---------------------------------------------------------------- 最小 YAML 解析

def parse_frontmatter(text):
    """返回 (ok, data, raw_block, body, error)。

    不依赖 PyYAML。实现 OKF 规范用到的 YAML 子集：
    标量、列表、嵌套映射（含 flow 风格 {a: b} 与 [a, b]）、
    列表项映射、块标量暂不展开。
    """
    if not text.startswith("---"):
        return False, {}, "", text, "文件未以 --- 开头，缺少 frontmatter"

    lines = text.split("\n")
    if lines[0].strip() != "---":
        return False, {}, "", text, "首行不是 ---"

    end = None
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return False, {}, "", text, "frontmatter 未闭合（缺第二个 ---）"

    raw = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    try:
        data = _parse_yaml_block(raw.split("\n"), 0, 0)[0]
    except Exception as e:  # noqa: BLE001
        return False, {}, raw, body, "YAML 解析失败: %s" % e
    return True, data, raw, body, None


def _scalar(s):
    s = s.strip()
    if not s:
        return ""
    if (s[0] == s[-1] == '"' and len(s) >= 2) or (s[0] == s[-1] == "'" and len(s) >= 2):
        return s[1:-1]
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", ""):
        return None
    if re.match(r"^-?\d+$", s):
        return int(s)
    if re.match(r"^-?\d*\.\d+$", s):
        return float(s)
    if s.startswith("[") and s.endswith("]"):
        return _parse_flow_seq(s[1:-1])
    if s.startswith("{") and s.endswith("}"):
        return _parse_flow_map(s[1:-1])
    return s


def _split_flow(body):
    """按逗号切分 flow 集合，跳过嵌套括号与引号。"""
    out, buf, depth, quote = [], "", 0, None
    for ch in body:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf += ch
        elif ch in "[{":
            depth += 1
            buf += ch
        elif ch in "]}":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(buf)
    return [x.strip() for x in out if x.strip()]


def _parse_flow_seq(body):
    return [_scalar(x) for x in _split_flow(body)]


def _parse_flow_map(body):
    out = {}
    for part in _split_flow(body):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = _scalar(v)
    return out


def _parse_yaml_block(lines, i, indent):
    """解析缩进块。返回 (value, next_index)。"""
    # 列表
    if i < len(lines) and lines[i].strip().startswith("- "):
        return _parse_seq(lines, i, indent)
    return _parse_map(lines, i, indent)


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


def _parse_seq(lines, i, indent):
    out = []
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cur = _indent_of(raw)
        if cur < indent:
            break
        if cur > indent:
            break
        body = raw.strip()[1:].strip()
        if not body:
            i += 1
            continue
        # 行内映射项 {a: b, c: d}
        if body.startswith("{"):
            out.append(_parse_flow_map(body[1:-1]))
            i += 1
            continue
        # 形如 - key: value  →  嵌套映射
        if ":" in body and not body.startswith("["):
            k, v = body.split(":", 1)
            item = {}
            child_indent = cur + 2
            if v.strip():
                item[k.strip()] = _scalar(v)
                i += 1
            else:
                i += 1
                sub, i = _parse_yaml_block(lines, i, child_indent)
                item[k.strip()] = sub
            # 该列表项后续更深缩进的行
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    i += 1
                    continue
                ni = _indent_of(nxt)
                if ni <= cur:
                    break
                sub, i = _parse_yaml_block(lines, i, ni)
                if isinstance(sub, dict):
                    item.update(sub)
                else:
                    break
            out.append(item)
            continue
        out.append(_scalar(body))
        i += 1
    return out, i


def _parse_map(lines, i, indent):
    out = {}
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cur = _indent_of(raw)
        if cur < indent:
            break
        if cur > indent:
            i += 1
            continue
        line = raw.strip()
        if line.startswith("- "):
            break
        if ":" not in line:
            i += 1
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if v:
            out[k] = _scalar(v)
            i += 1
        else:
            i += 1
            if i < len(lines):
                ni = _indent_of(lines[i])
                if lines[i].strip().startswith("- ") and ni >= cur:
                    sub, i = _parse_seq(lines, i, ni)
                    out[k] = sub
                elif ni > cur:
                    sub, i = _parse_map(lines, i, ni)
                    out[k] = sub
                else:
                    out[k] = None
            else:
                out[k] = None
    return out, i


# ---------------------------------------------------------------- 采集

def read_text(path):
    for enc in ("utf-8", "utf-8-sig", "gbk"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".trash",
             ".okf-backup", "attachments", "09 attachments", "09 资源",
             # agent 工作区元数据，不属于知识库内容
             ".workbuddy", ".agents", ".claude", ".codebuddy"}


def collect_markdown(bundle_root):
    out = []
    for dirpath, dirnames, filenames in os.walk(bundle_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


# ---------------------------------------------------------------- 检查项

def check_file(path, bundle_root, rel):
    """返回该文件的问题列表。"""
    issues = []
    text = read_text(path)
    if text is None:
        return [{"level": "P0", "rule": "encoding",
                 "msg": "无法以 utf-8/gbk 解码"}], None

    reserved = os.path.basename(path) in RESERVED
    is_schema = rel in SCHEMA_FILES
    # sources/ 是 LLM-Wiki 的不可变原始层：OKF 合规要求针对概念页，
    # 原始资料保持原样（且不允许改写），因此不做 frontmatter 校验。
    in_sources = rel.startswith("sources/")
    # templates/ 是模板（含空占位），不参与体检
    in_template = rel.startswith("templates/")
    # references/ 是外部资料与规范原文的镜像，不是本库产出的知识页。
    # 它们本身可能包含 v0.1 遗留写法（规范原文即如此），不该按 OKF 合规判定。
    in_reference = rel.startswith("references/")

    ok, fm, raw, body, err = parse_frontmatter(text)
    if not ok:
        if reserved or is_schema or in_template or in_reference:
            # index.md 允许无 frontmatter（bundle 根可带 okf_version）
            # schema 文件（索引/日志/指南）不是概念页，同样豁免
            return [], {"rel": rel, "body": body, "fm": {}, "reserved": reserved,
                        "schema": is_schema}
        if in_sources:
            return [], {"rel": rel, "body": body, "fm": {}, "reserved": False,
                        "in_sources": True}
        issues.append({"level": "P0", "rule": "frontmatter-parse",
                       "msg": err})
        return issues, {"rel": rel, "body": body, "fm": {}, "reserved": False}

    info = {"rel": rel, "body": body, "fm": fm, "reserved": reserved,
            "raw": raw, "in_sources": in_sources, "schema": is_schema,
            "template": in_template, "reference": in_reference}

    if reserved:
        if rel == "index.md" and set(fm) - {"okf_version"}:
            issues.append({
                "level": "P1", "rule": "index-frontmatter",
                "msg": "index.md 只允许 okf_version 一个键，实际有: %s"
                       % ", ".join(sorted(set(fm) - {"okf_version"}))})
        return issues, info

    if in_sources or is_schema or in_template or in_reference:
        return issues, info

    # 合规：必须有非空 type
    t = fm.get("type")
    if t is None or (isinstance(t, str) and not t.strip()):
        issues.append({"level": "P0", "rule": "type-missing",
                       "msg": "缺 frontmatter type（OKF §11 唯一必填项）"})

    # type 拼写漂移
    if isinstance(t, str) and t.strip() and t.strip() not in KNOWN_TYPES:
        issues.append({
            "level": "P2", "rule": "type-unknown",
            "msg": "type '%s' 不在本 bundle 词表，确认是否拼写漂移或该入表" % t.strip()})

    # status 取值
    st = fm.get("status")
    if st is not None and st not in VALID_STATUS:
        issues.append({"level": "P1", "rule": "status-invalid",
                       "msg": "status '%s' 非法，应为 draft/stable/deprecated" % st})

    # v0.1 遗留字段
    for lk in LEGACY_KEYS:
        if lk in fm:
            issues.append({
                "level": "P1", "rule": "legacy-field",
                "msg": "v0.1 遗留字段 '%s'，v0.2 应用 generated.at" % lk})
    if re.search(r"^#+\s*Citations\s*$", body, re.M | re.I):
        issues.append({
            "level": "P1", "rule": "legacy-field",
            "msg": "正文 '# Citations' 已被 frontmatter sources 取代（v0.2）"})

    # generated / verified 结构与 actor
    gen = fm.get("generated")
    if gen is not None:
        if not isinstance(gen, dict):
            issues.append({"level": "P1", "rule": "generated-shape",
                           "msg": "generated 应为 { by, at } 映射"})
        else:
            if not gen.get("by"):
                issues.append({"level": "P1", "rule": "generated-by",
                               "msg": "generated.by 条目内必填"})
            elif isinstance(gen.get("by"), str) and not ACTOR_RE.match(gen["by"].strip()):
                issues.append({
                    "level": "P1", "rule": "actor-format",
                    "msg": "generated.by '%s' 不符合 actor 约定 "
                           "(human:<id> / <producer>/<version> / process:<id>)" % gen["by"]})
            at = gen.get("at")
            if at and isinstance(at, str) and not ISO_RE.match(at.strip()):
                issues.append({"level": "P1", "rule": "timestamp-format",
                               "msg": "generated.at '%s' 非 ISO 8601" % at})

    ver = fm.get("verified")
    if ver is not None:
        vs = ver if isinstance(ver, list) else [ver]
        if not vs:
            issues.append({"level": "P2", "rule": "verified-empty",
                           "msg": "verified 为空列表，等同无验证（unverified）"})
        for v in vs:
            if not isinstance(v, dict):
                issues.append({"level": "P1", "rule": "verified-shape",
                               "msg": "verified 条目应为 { by, at } 映射"})
                continue
            if not v.get("by"):
                issues.append({"level": "P1", "rule": "verified-by",
                               "msg": "verified[].by 必填"})
            elif isinstance(v.get("by"), str) and not ACTOR_RE.match(v["by"].strip()):
                issues.append({
                    "level": "P1", "rule": "actor-format",
                    "msg": "verified[].by '%s' 不符合 actor 约定" % v["by"]})
            at = v.get("at")
            if at and isinstance(at, str) and not ISO_RE.match(at.strip()):
                issues.append({"level": "P1", "rule": "timestamp-format",
                               "msg": "verified[].at '%s' 非 ISO 8601" % at})

    # stale_after
    sa = fm.get("stale_after")
    if sa is not None:
        if not isinstance(sa, str) or not ISO_RE.match(sa.strip()):
            issues.append({"level": "P1", "rule": "stale-format",
                           "msg": "stale_after '%s' 非 ISO 8601 绝对时刻" % sa})

    # sources
    srcs = fm.get("sources")
    if isinstance(srcs, dict) and not srcs:
        # 迁移脚本产出的 `sources:\n  []` 会被解析成空 dict，视作空列表
        srcs = []
    if srcs is not None and srcs != [] and not isinstance(srcs, list):
        issues.append({"level": "P1", "rule": "sources-shape",
                       "msg": "sources 应为列表，实际为 %s" % type(srcs).__name__})
    elif isinstance(srcs, list):
        ids = set()
        for s in srcs:
            if isinstance(s, str):
                issues.append({
                    "level": "P1", "rule": "sources-item",
                    "msg": "sources 条目应为映射（含 resource），发现裸字符串 '%s'" % s})
                continue
            if not isinstance(s, dict):
                issues.append({"level": "P1", "rule": "sources-item",
                               "msg": "sources 条目类型异常: %r" % (s,)})
                continue
            if not s.get("resource"):
                issues.append({"level": "P1", "rule": "sources-resource",
                               "msg": "sources[].resource 条目内必填"})
            lm = s.get("last_modified")
            if lm and isinstance(lm, str) and not ISO_RE.match(lm.strip()):
                issues.append({"level": "P1", "rule": "timestamp-format",
                               "msg": "sources[].last_modified '%s' 非 ISO 8601 带时区格式" % lm})
            sid = s.get("id")
            if sid:
                if sid in ids:
                    issues.append({"level": "P1", "rule": "sources-id-dup",
                                   "msg": "sources id 重复: '%s'" % sid})
                ids.add(sid)

    # 脚注引用与 sources[].id 对应
    if isinstance(srcs, list) and srcs:
        declared = {s.get("id") for s in srcs
                    if isinstance(s, dict) and s.get("id")}
        used = set(FOOTNOTE_REF.findall(body))
        defined = set(FOOTNOTE_DEF.findall(body))
        for u in sorted(used - declared):
            if u in defined:
                issues.append({
                    "level": "P2", "rule": "footnote-unlinked",
                    "msg": "脚注 [^%s] 在正文定义但 sources 中无对应 id" % u})
        for d in sorted(declared - used):
            issues.append({
                "level": "P2", "rule": "source-unused",
                "msg": "sources id '%s' 未被任何脚注引用" % d})

    # 结构完整性（LLM-Wiki 页面格式）
    if isinstance(t, str) and t.strip() in ("Concept", "Hub", "Tech Design",
                                             "Project", "ADR", "Playbook"):
        need = ["概述", "相关"]
        for n in need:
            if ("## " + n) not in body:
                issues.append({
                    "level": "P2", "rule": "section-missing",
                    "msg": "缺 '## %s' 章节（保持本库页面格式一致）" % n})
        if not fm.get("description"):
            issues.append({"level": "P2", "rule": "desc-missing",
                           "msg": "缺 description，索引与搜索摘要会为空"})

    return issues, info


def check_links(infos, bundle_root):
    """断链 + 孤儿页。返回 (issues_by_rel, stats)。"""
    issues_by_rel = defaultdict(list)
    names = defaultdict(list)
    for rel, info in infos.items():
        if info.get("reserved"):
            continue
        stem = os.path.basename(rel)[:-3]
        names[stem.lower()].append(rel)

    inbound = defaultdict(set)
    unresolved_wiki = defaultdict(list)

    # 「待补页面」占位：知识库里常见「待投放素材」的规划式链接，
    # 不是真断链，降级为 P2 提示。
    PLACEHOLDER = re.compile(r"(待补|待写|待投放|TODO|待建)")

    for rel, info in infos.items():
        # templates/ 是含空占位的模板，不参与断链与入链统计
        if info.get("template"):
            continue
        body = info.get("body") or ""
        base = os.path.dirname(rel)

        # 去掉代码围栏与行内代码，避免把示例里的链接当真实链接
        stripped = re.sub(r"```.*?```", "", body, flags=re.S)
        stripped = re.sub(r"`[^`\n]*`", "", stripped)

        targets = []
        for m in re.finditer(r"(!?)\[\[([^\]|#]+)", stripped):
            targets.append(("wiki", m.group(2).strip(), m.group(1) == "!"))
        for label, tgt in MDLINK.findall(stripped):
            t = tgt.strip()
            if t.startswith(("http://", "https://", "mailto:", "#", "obsidian://")):
                continue
            targets.append(("md", t, False))

        for kind, t, embedded in targets:
            if kind == "wiki":
                # 附件嵌入/链接不算断链
                if os.path.splitext(t)[1].lower() in ATTACH_EXT:
                    continue
                key = t.lower().replace("\\", "/")
                hit = names.get(os.path.basename(key).lower())
                if hit:
                    for h in hit:
                        if h != rel:
                            inbound[h].add(rel)
                else:
                    unresolved_wiki[rel].append(("[[%s]]" % t, PLACEHOLDER.search(t)))
                continue

            t = t.split("#")[0].split("?")[0]
            if not t:
                continue
            if os.path.splitext(t)[1].lower() in ATTACH_EXT:
                continue
            if t.startswith("/"):
                cand = os.path.join(bundle_root, t.lstrip("/"))
            else:
                cand = os.path.normpath(os.path.join(bundle_root, base, t))
            if os.path.isdir(cand):
                cand_idx = os.path.join(cand, "index.md")
                target_rel = os.path.relpath(cand_idx, bundle_root).replace("\\", "/")
                if os.path.exists(cand_idx):
                    inbound[target_rel].add(rel)
                    continue
                # 指向 sources/ 的目录：原始资料层不要求每层都有 index，
                # 目录存在即可（P2 提示）
                lvl = "P2" if t.lstrip("./").replace("\\", "/").startswith("sources") else "P1"

                issues_by_rel[rel].append({
                    "level": lvl, "rule": "link-dir-no-index",
                    "msg": "目录链接无 index.md: %s" % t})
                continue
            if not os.path.exists(cand):
                # 允许指向 bundle 外的本地绝对路径
                if t.startswith(("D:/", "D:\\", "C:/", "C:\\")):
                    continue
                issues_by_rel[rel].append({
                    "level": "P1", "rule": "link-broken",
                    "msg": "断链: %s" % t})
                continue
            target_rel = os.path.relpath(cand, bundle_root).replace("\\", "/")
            if target_rel != rel:
                inbound[target_rel].add(rel)

    for rel, links in unresolved_wiki.items():
        # Hub 页（分类枢纽）按规划枚举待写主题，未落地是正常的
        is_hub = (infos[rel].get("fm") or {}).get("type") == "Hub"
        for l, is_placeholder in links:
            if is_placeholder:
                issues_by_rel[rel].append({
                    "level": "P2", "rule": "link-placeholder",
                    "msg": "占位链接（页面尚未写）: %s" % l})
            elif is_hub:
                issues_by_rel[rel].append({
                    "level": "P2", "rule": "link-roadmap",
                    "msg": "Hub 页规划主题（尚未撰写）: %s" % l})
            else:
                issues_by_rel[rel].append({
                    "level": "P1", "rule": "link-broken",
                    "msg": "断链（无匹配页面）: %s" % l})

    orphans = []
    for rel, info in infos.items():
        if (info.get("reserved") or info.get("schema") or info.get("template")
                or rel.startswith("sources/") or rel.startswith("wiki/schema/")
                or rel.startswith("references/")):
            continue
        if not inbound.get(rel):
            orphans.append(rel)

    return issues_by_rel, orphans, inbound


def check_index_coverage(infos, bundle_root):
    """索引遗漏：概念页是否在某个 index/索引 中被提及。"""
    index_files = []
    for rel in infos:
        base = os.path.basename(rel)
        if base == "index.md" or base == "索引.md":
            index_files.append(rel)
    if not index_files:
        return {}

    blob = "\n".join((infos[r].get("body") or "") for r in index_files)
    blob_l = blob.lower()
    issues = defaultdict(list)
    for rel, info in infos.items():
        if (info.get("reserved") or info.get("schema") or info.get("template")
                or rel.startswith("sources/") or rel.startswith("references/")):
            continue
        stem = os.path.basename(rel)[:-3]
        if stem.lower() not in blob_l and rel.lower() not in blob_l:
            issues[rel].append({
                "level": "P1", "rule": "index-missing",
                "msg": "未在索引中提及（%s）" % ("/".join(index_files) or "无索引文件")})
    return issues


def check_stale(infos, today):
    issues = defaultdict(list)
    for rel, info in infos.items():
        sa = (info.get("fm") or {}).get("stale_after")
        if not isinstance(sa, str):
            continue
        d = sa.strip()[:10]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", d) and d < today:
            issues[rel].append({
                "level": "P1", "rule": "stale",
                "msg": "已过 stale_after (%s)，内容可能失效" % d})
    return issues


# ---------------------------------------------------------------- 输出

LEVEL_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def render(issues_by_rel, orphans, stats, root, as_json):
    if as_json:
        print(json.dumps({
            "bundle_root": root,
            "stats": stats,
            "orphans": sorted(orphans),
            "issues": {k: v for k, v in sorted(issues_by_rel.items()) if v},
        }, ensure_ascii=False, indent=2))
        return

    print("=" * 62)
    print("OKF 知识库体检  %s" % root)
    print("=" * 62)
    print("扫描 %d 个 markdown，%d 个概念页" % (stats["files"], stats["concepts"]))
    print()

    if not issues_by_rel and not orphans:
        print("无问题。知识库状态健康。")
        return

    by_level = defaultdict(list)
    for rel, items in issues_by_rel.items():
        for it in items:
            by_level[it["level"]].append((rel, it))

    label = {"P0": "P0 破损（必修）", "P1": "P1 失真（应修）", "P2": "P2 优化（可选）"}
    for lv in ("P0", "P1", "P2"):
        rows = by_level.get(lv)
        if not rows:
            continue
        print("--- %s  %d 项 ---" % (label[lv], len(rows)))
        rows.sort(key=lambda x: (LEVEL_ORDER[x[1]["level"]], x[0]))
        for rel, it in rows:
            print("  [%s] %-14s %s" % (it["rule"], rel, it["msg"]))
        print()

    if orphans:
        print("--- 孤儿页（无入链）  %d 个 ---" % len(orphans))
        for rel in sorted(orphans):
            print("  %s" % rel)
        print()

    counts = {lv: len(by_level.get(lv, [])) for lv in ("P0", "P1", "P2")}
    print("-" * 62)
    print("合计  P0=%d  P1=%d  P2=%d  孤儿=%d"
          % (counts["P0"], counts["P1"], counts["P2"], len(orphans)))
    print("只报告，未修改任何文件。")


def main():
    ap = argparse.ArgumentParser(description="OKF v0.2 知识库体检")
    ap.add_argument("bundle_root", nargs="?",
                    help="不传则依次尝试: 当前目录 → ~/.agent-wiki.json 的 wikiRoot")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="有 P0 时退出码 1")
    args = ap.parse_args()

    root, source = resolve_bundle_root(args.bundle_root)
    if not root:
        print("无法确定 bundle_root。请显式传入，或创建 ~/.agent-wiki.json:",
              file=sys.stderr)
        print('  { "wikiRoot": "<bundle 绝对路径>" }', file=sys.stderr)
        return 2
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print("bundle_root 不存在: %s" % root, file=sys.stderr)
        return 2
    print("bundle_root: %s  (来源: %s)" % (root, source))

    import datetime
    today = datetime.date.today().isoformat()

    files = collect_markdown(root)
    issues_by_rel = defaultdict(list)
    infos = {}

    for path in files:
        rel = os.path.relpath(path, root).replace("\\", "/")
        iss, info = check_file(path, root, rel)
        if iss:
            issues_by_rel[rel].extend(iss)
        if info:
            infos[rel] = info

    link_issues, orphans, _ = check_links(infos, root)
    for rel, items in link_issues.items():
        issues_by_rel[rel].extend(items)
    for rel, items in check_index_coverage(infos, root).items():
        issues_by_rel[rel].extend(items)
    for rel, items in check_stale(infos, today).items():
        issues_by_rel[rel].extend(items)

    stats = {
        "files": len(files),
        "concepts": len([r for r, i in infos.items() if not i.get("reserved")]),
        "sources": len([r for r in infos if r.startswith("sources/")]),
    }

    render(issues_by_rel, orphans, stats, root, args.json)

    has_p0 = any(it["level"] == "P0"
                 for items in issues_by_rel.values() for it in items)
    return 1 if (args.strict and has_p0) else 0


if __name__ == "__main__":
    sys.exit(main())
