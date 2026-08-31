#!/usr/bin/env python3
"""Patch a freshly-installed R prefix so it's genuinely relocatable with zero extra tooling: R's own launchers hardcode the build-time path and ignore R_HOME, so this rewrites them in place."""

import re
import sys
from pathlib import Path

R_SH_FILES = {
    "bin/R": "../lib/R",
    "lib/R/bin/R": "..",
}

RSCRIPT_WRAPPER = """#!/bin/sh
DIR=$(cd "$(dirname "$0")" && pwd)
case "$1" in
  ""|-*) exec "$DIR/R" --no-echo --no-restore "$@" ;;
  *) script=$1; shift; exec "$DIR/R" --no-echo --no-restore --file="$script" --args "$@" ;;
esac
"""

RSCRIPT_FILES = ["bin/Rscript", "lib/R/bin/Rscript"]


def patch_r_sh(path: Path, rel_to_r_home: str) -> None:
    content = path.read_text()

    pattern = re.compile(r"R_HOME_DIR=.*?\nfi\n", re.DOTALL)
    replacement = f'R_HOME_DIR="$(cd "$(dirname "$0")/{rel_to_r_home}" && pwd)"\n'
    content, n = pattern.subn(replacement, content, count=1)
    if n != 1:
        sys.exit(f"error: R_HOME_DIR block not found in {path} -- R's script format may have changed, review before proceeding")

    for var, sub in [("R_SHARE_DIR", "share"), ("R_INCLUDE_DIR", "include"), ("R_DOC_DIR", "doc")]:
        content, n = re.subn(rf"{var}=\S+", f'{var}="${{R_HOME_DIR}}/{sub}"', content, count=1)
        if n != 1:
            sys.exit(f"error: {var} assignment not found in {path} -- R's script format may have changed, review before proceeding")

    path.write_text(content)
    print(f"patched {path}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <r-install-prefix>")

    prefix = Path(sys.argv[1])

    for rel_path, rel_to_r_home in R_SH_FILES.items():
        path = prefix / rel_path
        if not path.exists():
            sys.exit(f"error: expected {path} to exist")
        patch_r_sh(path, rel_to_r_home)

    for rel_path in RSCRIPT_FILES:
        path = prefix / rel_path
        if not path.exists():
            sys.exit(f"error: expected {path} to exist")
        path.unlink()
        path.write_text(RSCRIPT_WRAPPER)
        path.chmod(0o755)
        print(f"replaced {path} with a relocatable wrapper")


if __name__ == "__main__":
    main()
