#!/usr/bin/env python3
"""Install only the eleven bundled skills, refusing to overwrite existing skills."""
import argparse
import os
import shutil
from pathlib import Path

NAMES = ('academic-writing', 'argument-architect', 'context-pack-builder', 'manuscript-auditor', 'manuscript-editor', 'paper-dissector', 'source-harvester', 'scientific-figure', 'research-harness', 'ovito-structure', 'ansatz-slide')


def install(destination):
    source = Path(__file__).resolve().parent / "skills"
    destination = Path(destination).expanduser()
    conflicts = [str(destination / name) for name in NAMES if (destination / name).exists()]
    if conflicts:
        raise FileExistsError("Existing skills are not overwritten: " + ", ".join(conflicts))
    for name in NAMES:
        if not (source / name / "SKILL.md").is_file():
            raise FileNotFoundError("Missing skill: " + name)
    destination.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        shutil.copytree(source / name, destination / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print("Installed: " + str(destination / name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", default=str(Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"))
    args = parser.parse_args()
    install(args.dest)
