# -*- coding: utf-8 -*-
"""建骨架脚本与文档自洽的测试。"""

from __future__ import annotations

import re

from conftest import SKILL_ROOT


def test_init_creates_skeleton(project):
    for rel in (
        "state",
        "workspace/volumes",
        "workspace/acts",
        "workspace/outlines",
        "workspace/drafts",
        "workspace/chapters",
        "workspace/summaries",
    ):
        assert (project / rel).is_dir(), rel
    for rel in (
        "state/author_persona.md",
        "state/story_bible.md",
        "state/current_state.md",
        "state/memory.md",
    ):
        assert (project / rel).is_file(), rel


def test_init_is_idempotent(project, init_project):
    (project / "state" / "memory.md").write_text("已填写", encoding="utf-8")
    assert init_project.main([str(project)]) == 0
    assert (project / "state" / "memory.md").read_text(encoding="utf-8") == "已填写"


def test_init_rejects_file_as_root(tmp_path, init_project):
    target = tmp_path / "已经是文件"
    target.write_text("x", encoding="utf-8")
    assert init_project.main([str(target)]) == 1


def test_skill_description_matches_manifest():
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    manifest = (SKILL_ROOT / "manifest.yaml").read_text(encoding="utf-8")
    skill_desc = re.search(r"^description:\s*(.+)$", skill, re.MULTILINE).group(1).strip()
    manifest_desc = re.search(r'^description:\s*"(.+)"$', manifest, re.MULTILINE).group(1).strip()
    assert skill_desc == manifest_desc


def test_referenced_files_exist():
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for rel in set(re.findall(r"(?:references|scripts|assets)/[\w./-]+\.(?:md|py)", skill)):
        assert (SKILL_ROOT / rel).is_file(), rel
