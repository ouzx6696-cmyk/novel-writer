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
        "state/story_foundation.md",
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


def test_persona_has_default_identity():
    persona = (SKILL_ROOT / "assets" / "templates" / "author_persona.md").read_text(encoding="utf-8")
    assert "我是一名网络小说作者，擅长番茄小说风格，正在创作一本" in persona
    assert "七、来源与修订" in persona


def test_no_trial_writing_left():
    """试写模块已整体移除，文档与模板不得残留。"""
    targets = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "README.md",
        SKILL_ROOT / "manifest.yaml",
        SKILL_ROOT / "scripts" / "init_project.py",
        SKILL_ROOT / "references" / "style_report_mapping.md",
        SKILL_ROOT / "assets" / "templates" / "author_persona.md",
        SKILL_ROOT / "assets" / "templates" / "memory.md",
        SKILL_ROOT / "assets" / "examples" / "persona_translation_example.md",
    ]
    for path in targets:
        assert "试写" not in path.read_text(encoding="utf-8"), path.name
