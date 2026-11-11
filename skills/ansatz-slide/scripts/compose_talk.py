#!/usr/bin/env python3
"""Compose normal speaker notes from ordered, source-bound spoken blocks.

This is a text projection, not a scientific or audience-comprehension validator.
The returned pages' notes are consumed by the existing page authoring code.
No deck, source paper or input mapping is modified.
"""
import argparse
import copy
import json
from pathlib import Path


def compose(mapping):
    result = copy.deepcopy(mapping)
    pages = result.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("pages must be a nonempty ordered list")
    normal, audit = [], ["# Spoken evidence projection", "", "Unassessed: source fidelity, comprehension and visible placement require actual review.", ""]
    seen = set()
    for position, page in enumerate(pages, 1):
        page_id = page.get("id", str(position))
        if page_id in seen:
            raise ValueError(f"duplicate page id: {page_id}")
        seen.add(page_id)
        title = page.get("title", page_id)
        blocks = page.get("notes_blocks")
        if blocks is None:
            if not isinstance(page.get("notes"), str) or not page["notes"].strip():
                raise ValueError(f"{page_id}: provide notes or notes_blocks")
        else:
            if "notes" in page:
                raise ValueError(f"{page_id}: remove stale notes; notes_blocks is authoritative")
            if not isinstance(blocks, list) or not blocks:
                raise ValueError(f"{page_id}: notes_blocks must be nonempty")
            spoken = []
            for number, block in enumerate(blocks, 1):
                text = block.get("spoken")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError(f"{page_id} block {number}: spoken text required")
                spoken.append(text)
                if block.get("kind") == "evidence":
                    source = block.get("source")
                    if not isinstance(source, str) or not source.strip():
                        raise ValueError(f"{page_id} block {number}: source locator required")
                    audit += [f"## {page_id} / {title} / block {number}", "", f"Source: {source}", "", f"Spoken: {text}", ""]
                    if block.get("visible_text"):
                        audit += [f"Intended visible text (not verified): {block['visible_text']}", ""]
                    if block.get("source_excerpt"):
                        audit += [f"Source excerpt for manual comparison: {block['source_excerpt']}", ""]
            page["notes"] = "\n\n".join(spoken)
        normal += [f"## {position:02d} · {title}", "", page["notes"], ""]
    return result, "\n".join(normal), "\n".join(audit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="new output directory")
    args = parser.parse_args()
    mapping, normal, audit = compose(json.loads(args.mapping.read_text(encoding="utf-8")))
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "source-map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out / "speaker-notes.md").write_text(normal, encoding="utf-8")
    (args.out / "evidence-projection.md").write_text(audit, encoding="utf-8")


if __name__ == "__main__":
    main()
