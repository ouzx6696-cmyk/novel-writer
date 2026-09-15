#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelCraft 项目初始化：建目录骨架，复制四份状态模板。已存在文件不覆盖。"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"

DIRS = [
    "state",
    "workspace/volumes",
    "workspace/acts",
    "workspace/outlines",
    "workspace/drafts",
    "workspace/chapters",
    "workspace/summaries",
]

TEMPLATES = {
    "author_persona.md": "state/author_persona.md",
    "story_foundation.md": "state/story_foundation.md",
    "current_state.md": "state/current_state.md",
    "memory.md": "state/memory.md",
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="NovelCraft 项目初始化")
    parser.add_argument("root", nargs="?", default=".", help="项目根目录")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if root.exists() and not root.is_dir():
        print(f"项目根路径不是目录: {root}")
        return 1

    missing = [name for name in TEMPLATES if not (TEMPLATE_DIR / name).is_file()]
    if missing:
        print(f"模板缺失: {missing}")
        return 1

    created: list[str] = []
    skipped: list[str] = []
    root.mkdir(parents=True, exist_ok=True)
    for rel in DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)

    for name, rel in TEMPLATES.items():
        target = root / rel
        if target.exists():
            skipped.append(rel)
        else:
            shutil.copyfile(TEMPLATE_DIR / name, target)
            created.append(rel)

    print(f"项目根: {root.as_posix()}")
    print(f"新建: {created if created else '无'}")
    print(f"跳过: {skipped if skipped else '无'}")
    print("下一步: 填 state/author_persona.md 与 state/story_foundation.md → 写第一卷纲和第一幕纲 → 把 memory.md 项目状态改为 可写。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
