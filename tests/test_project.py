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


def test_story_foundation_has_world_setting():
    foundation = (SKILL_ROOT / "assets" / "templates" / "story_foundation.md").read_text(encoding="utf-8")
    assert "世界观与规则" in foundation
    for level in ("世界级", "社会级", "个人级"):
        assert level in foundation, level
    # 三要素必须写在模板里，缺代价读者就会问"那就用啊"
    assert "代价" in foundation
    assert "真缺点" in foundation


def test_story_foundation_has_main_line():
    """全书主线必须有一句话的落点——卷纲要回答'这是主线哪一步'，主线本身不能无处可写。"""
    foundation = (SKILL_ROOT / "assets" / "templates" / "story_foundation.md").read_text(encoding="utf-8")
    assert "全书主线" in foundation
    assert "终点画面" in foundation


def test_volume_outline_maps_ladder_to_acts_not_chapters():
    """冲突阶梯落在幕级，不能越过幕直接对应章。"""
    volume = (SKILL_ROOT / "assets" / "templates" / "volume_outline.md").read_text(encoding="utf-8")
    assert "对应幕" in volume
    assert "对应章" not in volume


def test_volume_outline_has_craft_fields():
    volume = (SKILL_ROOT / "assets" / "templates" / "volume_outline.md").read_text(encoding="utf-8")
    for field in ("本卷在主线哪一步", "对抗力量", "输不起", "情绪走向", "主导驱动力", "信息差", "冲突阶梯"):
        assert field in volume, field


def test_init_runs_before_filling_state():
    """路线一必须先跑 init 再填文件；顺序写反会让前三步无处落笔。"""
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    route = skill.split("路线一")[1].split("路线二")[0]
    assert route.index("init_project.py") < route.index("写人格")


def test_skill_and_readme_route_one_agree():
    """两个文档的路线一步骤必须同构，避免只说给一边听。"""
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    readme = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
    for text in (skill, readme):
        route = text.split("路线一")[1].split("路线二")[0]
        assert "落盘" in route and "读人格来源" in route and "写故事根基" in route


def test_references_exist_and_are_linked():
    for name in ("outline_craft.md", "setting_craft.md", "anti_ai.md", "style_report_mapping.md"):
        assert (SKILL_ROOT / "references" / name).is_file(), name
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "references/outline_craft.md" in skill
    assert "references/setting_craft.md" in skill
