#!/usr/bin/env python3
"""CLI entry point for ALPS Markdown Profile v1."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from alps_markdown import (  # noqa: E402,F401
    PROFILE_VERSION,
    Diagnostic,
    DocumentIR,
    ParseResult,
    check_asset,
    check_document,
    check_pair,
    main,
    parse_asset,
    validate_ir,
)


if __name__ == "__main__":
    raise SystemExit(main())
