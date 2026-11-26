#!/usr/bin/env python3
"""Check every relative link in every markdown file in the repo.

Usage:  python3 scripts/check_links.py
Exits 1 and lists broken links if a target file or folder is missing or a
link is an absolute path. Links to other websites are skipped.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def main():
    broken, checked = [], 0
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        text = re.sub(r"^(`{3,}).*?^\1", "", text, flags=re.S | re.M)  # skip code blocks
        for target in LINK.findall(text):
            if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            checked += 1
            path = unquote(target.split("#", 1)[0])
            if path.startswith("/"):
                broken.append((md, target, "absolute path"))
            elif path and not (md.parent / path).exists():
                broken.append((md, target, "missing"))
    for md, target, why in broken:
        print(f"{md.relative_to(ROOT)}: {target} ({why})")
    print(f"Checked {checked} links; {len(broken)} broken.")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
