# -*- coding: utf-8 -*-
"""pytest 公共夹具：按路径加载脚本，构造最小项目。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"nw_{name}", SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"nw_{name}"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def init_project():
    return _load("init_project")


@pytest.fixture
def project(tmp_path, init_project) -> Path:
    root = tmp_path / "novel"
    assert init_project.main([str(root)]) == 0
    return root
