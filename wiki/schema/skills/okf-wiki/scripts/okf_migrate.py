#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
okf_migrate.py — 为既有知识页补 OKF frontmatter

用法:
    python okf_migrate.py <bundle_root> --dry-run     # 只预览
    python okf_migrate.py <bundle_root> --apply      # 实际写入
    python okf_migrate.py <bundle_root> --apply --only wiki/02-架构与设计

行为:
    - 只处理 wiki/ 与 concepts/ projects/ tech/ decisions/ people/ 下的 .md
    - 跳过 sources/（不可变层）、index.md / log.md（OKF 保留名）
    - 已有 frontmatter 的文件不动（幂等）
    - type 按目录约定推断，description 取正文首段引用块或首句
    - sources 从正文「## 来源」小节的 markdown 链接反推
    - 写前自动备份到 <bundle>/.okf-backup/

推断规则:
    wiki/0X-*/xxx.md   名为「分类名」的枢纽页 → Hub，否则 Concept
    concepts/           Concept
    projects/           Project
    tech/               Tech Design
    decisions/          ADR
    people/             Person
    references/         Reference
    其它                Concept
"""

import argparse
import datetime
import os
import re
import shutil
import sys

# 目录 → type 映射
TYPE_BY_DIR = [
    ("concepts/", "Concept"),
    ("projects/", "Project"),
    ("tech/", "Tech Design"),
    ("decisions/", "ADR"),
    ("people/", "Person"),
    ("references/", "Reference"),
]

BACKUP_DIR = ".okf-backup"
AUTHOR = "human:laoli"
AGENT = "workbuddy/gpt-5"
CONFIG_NAME = ".agent-wiki.json"


def resolve_bundle_root(explicit=None):
    """按 SKILL.md §0 优先级解析 bundle_root: 参数 → cwd → ~/.agent-wiki.json。"""
    import json
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit)), "argument"

    def is_bundle(p):
        return bool(p) and os.path.isfile(os.path.join(p, "wiki", "索引.md"))

    for cand in (os.getcwd(),):
        if is_bundle(os.path.abspath(cand)):
            return os.path.abspath(cand), "cwd"

    cfg = os.path.join(os.path.expanduser("~"), CONFIG_NAME)
    if os.path.isfile(cfg):
        try:
            with open(cfg, encoding="utf-8") as fh:
                root = json.load(fh).get("wikiRoot")
            if root:
                return os.path.abspath(os.path.expanduser(root)), "config"
        except (OSError, ValueError) as exc:
            print("解析 %s 失败: %s" % (cfg, exc), file=sys.stderr)
    return None, None

WIKI_HUB_RE = re.compile(r"^##\s*(概述|简介|本分类|关于)")
BLOCKQUOTE_RE = re.compile(r"^>\s*(.+)$", re.M)
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
SOURCE_LINK_RE = re.compile(r"^\s*[-*]\s*\[([^\]]+)\]\(([^)]+)\)", re.M)


def read_text(path):
    for enc in ("utf-8", "utf-8-sig", "gbk"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


def has_frontmatter(text):
    return text.startswith("---") and len(text.split("\n", 2)) > 1 \
        and text.split("\n", 2)[1].strip() == "---"


def infer_type(rel):
    for prefix, t in TYPE_BY_DIR:
        if rel.startswith(prefix):
            return t
    if rel.startswith("wiki/"):
        stem = os.path.basename(rel)[:-3]
        # 分类枢纽页：文件名等于其所在分类名（去掉 NN- 前缀）
        folder = os.path.basename(os.path.dirname(rel))
        cat = re.sub(r"^\d+-", "", folder)
        if stem == cat:
            return "Hub"
    return "Concept"


def infer_description(text, rel):
    """取引用块首行，否则取 H1 后第一段首句。"""
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    m = BLOCKQUOTE_RE.search(body)
    if m:
        d = m.group(1).strip()
        d = re.sub(r"[*_`]", "", d)
        if len(d) > 10:
            return d[:120]
    # 取「## 概述」后的第一段
    m = re.search(r"^##\s*概述\s*$", body, re.M)
    seg = body[m.end():] if m else body
    m2 = H1_RE.search(body)
    if m2:
        seg = body[m2.end():]
    for para in seg.split("\n\n"):
        s = para.strip()
        if not s or s.startswith(("#", "|", "-", "*", ">", "```")):
            continue
        s = re.sub(r"[*_`]", "", s).replace("\n", " ")
        if len(s) > 10:
            return s[:120]
    return ""


def infer_tags(rel, t):
    tags = []
    if rel.startswith("wiki/"):
        m = re.match(r"wiki/(\d+)-(.+?)/", rel)
        if m:
            tags.append(m.group(2))
    m = re.search(r"\[([^\]]+)\]", rel)
    mapping = {"concepts/": "concept", "projects/": "project", "tech/": "tech",
               "decisions/": "decision", "people/": "person",
               "references/": "reference"}
    for k, v in mapping.items():
        if rel.startswith(k):
            tags.append(v)
    return tags


def infer_sources(text, bundle_root, rel):
    """从「## 来源」小节的 markdown 链接反推 sources。"""
    m = re.search(r"^##\s*来源\s*$", text, re.M)
    if not m:
        return []
    seg = text[m.end():]
    # 到下一个 H2 为止
    m2 = re.search(r"^##\s+", seg, re.M)
    if m2:
        seg = seg[:m2.start()]
    out = []
    base_dir = os.path.dirname(rel)
    for title, target in SOURCE_LINK_RE.findall(seg):
        if target.startswith(("http://", "https://")):
            res = target
        else:
            full = os.path.normpath(os.path.join(bundle_root, base_dir, target))
            res = "/" + os.path.relpath(full, bundle_root).replace("\\", "/")
        out.append({
            "id": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "src",
            "resource": res,
            "title": title,
        })
    return out


def build_frontmatter(rel, text, now_iso, mtime_iso, bundle_root):
    t = infer_type(rel)
    desc = infer_description(text, rel)
    srcs = infer_sources(text, bundle_root, rel)
    fm = ["---", "type: %s" % t]
    h1 = H1_RE.search(re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S))
    if h1:
        fm.append("title: %s" % h1.group(1).strip())
    if desc:
        clean_desc = desc.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()
        fm.append('description: "%s"' % clean_desc)
    tags = infer_tags(rel, t)
    if tags:
        fm.append("tags: [%s]" % ", ".join(tags))
    fm.append("status: stable")
    fm.append("generated: { by: %s, at: %s }" % (AGENT, now_iso))
    fm.append("sources:")
    if srcs:
        for s in srcs:
            fm.append("  - { id: %s, resource: %s, title: %s }"
                      % (s["id"], s["resource"], s["title"]))
    else:
        fm.append("  []")
    fm.append("---")
    return "\n".join(fm) + "\n"


def main():
    ap = argparse.ArgumentParser(description="为既有知识页补 OKF frontmatter")
    ap.add_argument("bundle_root", nargs="?",
                    help="不传则依次尝试: 当前目录 → ~/.agent-wiki.json 的 wikiRoot")
    ap.add_argument("--apply", action="store_true", help="实际写入（默认 dry-run）")
    ap.add_argument("--only", help="只处理该前缀路径")
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

    now = datetime.datetime.now().astimezone()
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    now_iso = now_iso[:-2] + ":" + now_iso[-2:]

    targets = []
    SKIP = {".git", ".obsidian", BACKUP_DIR, "attachments", "templates",
            "node_modules", "__pycache__", ".trash",
            ".workbuddy", ".agents", ".claude", ".codebuddy"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in sorted(filenames):
            if not fn.lower().endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if rel.startswith("sources/"):
                continue
            if fn in ("index.md", "log.md"):
                continue
            if rel.startswith("templates/"):
                continue
            # 知识库的 schema/入口文件：索引、操作日志、使用指南不属于概念页
            if rel in ("wiki/索引.md", "wiki/操作日志.md", "wiki/知识库使用指南.md"):
                continue
            if args.only and not rel.startswith(args.only):
                continue
            targets.append((full, rel))

    changed, skipped = [], []
    for full, rel in targets:
        text = read_text(full)
        if text is None:
            print("SKIP(编码) %s" % rel)
            continue
        if has_frontmatter(text):
            skipped.append(rel)
            continue
        mtime_iso = datetime.datetime.fromtimestamp(
            os.path.getmtime(full), now.astimezone().tzinfo
        ).strftime("%Y-%m-%dT%H:%M:%S%z")
        mtime_iso = mtime_iso[:-2] + ":" + mtime_iso[-2:]
        fm = build_frontmatter(rel, text, mtime_iso, now_iso, root)
        body = text
        new = fm + ("\n" + body if not body.startswith("\n") else body)
        changed.append((full, rel, new))

    print("=" * 60)
    print("OKF frontmatter 迁移  模式=%s" % ("APPLY" if args.apply else "DRY-RUN"))
    print("=" * 60)
    print("待迁移 %d 个，已有 frontmatter 跳过 %d 个\n" % (len(changed), len(skipped)))

    for full, rel, new in changed:
        t = re.search(r"^type: (.+)$", new, re.M)
        d = re.search(r"^description: (.+)$", new, re.M)
        n = len(re.findall(r"^  - \{ id:", new, re.M))
        print("  %-52s type=%-12s sources=%d" % (
            rel, t.group(1) if t else "?", n))
        if d:
            print("      %s" % d.group(1)[:70])

    if skipped:
        print("\n已有 frontmatter（不动）:")
        for rel in skipped:
            print("  %s" % rel)

    if not args.apply:
        print("\nDRY-RUN，未写入任何文件。加 --apply 执行。")
        return 0

    bdir = os.path.join(root, BACKUP_DIR)
    os.makedirs(bdir, exist_ok=True)
    for full, rel, new in changed:
        shutil.copy2(full, os.path.join(bdir, rel.replace("/", "__")))
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    print("\n已写入 %d 个文件。备份在 %s" % (len(changed), BACKUP_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
