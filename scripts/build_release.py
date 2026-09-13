#!/usr/bin/env python3
"""Build a deterministic source archive without caches or local artifacts."""
from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path

EXCLUDED_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_PARTS = {"tests", "test"}
# 白名单：只有这里列出的内容会进包，其余（缓存、.git、编辑器配置）一律不收。
INCLUDE_ROOTS = (
    "assets",
    "references",
    "scripts",
    "manifest.yaml",
    "SKILL.md",
    "README.md",
    "LICENSE",
)
PACKAGE_DIR_NAME = "novel-writer"

# SKILL.md 的 frontmatter 是版本权威；manifest.yaml 必须与它一致。
_SKILL_VERSION_RE = re.compile(r"^\s+version:\s*[\"']?([^\"'\s]+)", re.M)
_MANIFEST_VERSION_RE = re.compile(r"^version:\s*[\"']?([^\"'\s]+)", re.M)


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_NAMES or part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def _skill_version(source: Path):
    path = source / "SKILL.md"
    if not path.exists():
        return None
    frontmatter = "\n".join(path.read_text(encoding="utf-8").splitlines()[:15])
    match = _SKILL_VERSION_RE.search(frontmatter)
    return match.group(1) if match else None


def _assert_version_consistency(source: Path) -> None:
    """版本漂移会让人误判包内容，打包前先卡住。"""
    version = _skill_version(source)
    if version is None:
        raise SystemExit("版本不一致，拒绝打包：SKILL.md 未找到 version 声明")

    mismatches = []
    manifest_path = source / "manifest.yaml"
    if not manifest_path.exists():
        mismatches.append(f"manifest.yaml 缺失，无法校验（SKILL.md 为 {version}）")
    else:
        match = _MANIFEST_VERSION_RE.search(manifest_path.read_text(encoding="utf-8"))
        declared = match.group(1) if match else None
        if declared is None:
            mismatches.append(f"manifest.yaml 未找到 version 字段（SKILL.md 为 {version}）")
        elif declared != version:
            mismatches.append(f"manifest.yaml 声明 {declared}，SKILL.md 为 {version}（version 字段）")

    if mismatches:
        raise SystemExit("版本不一致，拒绝打包：\n  " + "\n  ".join(mismatches))


def build_archive(source: Path, output: Path) -> dict[str, object]:
    source = source.resolve()
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    _assert_version_consistency(source)
    files = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for root_name in INCLUDE_ROOTS:
            candidate = source / root_name
            if not candidate.exists():
                continue
            candidates = [candidate] if candidate.is_file() else sorted(candidate.rglob("*"))
            for path in candidates:
                if path.is_file() and should_include(path, source):
                    rel = Path(PACKAGE_DIR_NAME) / path.relative_to(source)
                    archive.write(path, rel.as_posix())
                    files.append(rel.as_posix())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {"output": str(output), "sha256": digest, "files": files}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build a clean novel-writer zip")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    output = args.output
    if output is None:
        version = _skill_version(args.source) or "0.0.0"
        output = args.source / "dist" / f"{PACKAGE_DIR_NAME}-{version}.zip"
    result = build_archive(args.source, output)
    print(f"output: {result['output']}")
    print(f"sha256: {result['sha256']}")
    print(f"files: {len(result['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
