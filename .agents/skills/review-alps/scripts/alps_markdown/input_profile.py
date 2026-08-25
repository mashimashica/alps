"""Bounded byte input and line normalization for the checker profile."""

from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO

from .model import (
    MAX_INPUT_BYTES,
    MAX_INPUT_LINES,
    MAX_LINE_BYTES,
    Diagnostic,
    InputResult,
    Severity,
    deterministic_diagnostics,
)


READ_CHUNK_BYTES = 64 * 1024
UTF8_BOM = b"\xef\xbb\xbf"


def _diagnostic(
    path: str,
    class_name: str,
    code: str,
    message: str,
    line: int | None = None,
) -> Diagnostic:
    return Diagnostic(class_name, code, Severity.ERROR, path, line, message)


def _line_number(data: bytes, offset: int) -> int:
    return data.count(b"\n", 0, offset) + 1


def _byte_length(value: bytes | bytearray | memoryview) -> int:
    if isinstance(value, memoryview):
        return value.nbytes
    return len(value)


def _first_bare_cr(data: bytes) -> int | None:
    offset = 0
    while True:
        offset = data.find(b"\r", offset)
        if offset < 0:
            return None
        if offset + 1 >= len(data) or data[offset + 1] != 0x0A:
            return offset
        offset += 2


def _line_limit_diagnostics(data: bytes, path: str) -> tuple[Diagnostic, ...]:
    if not data:
        return ()

    diagnostics: list[Diagnostic] = []
    found_line_too_long = False
    found_line_limit = False
    line = 1
    start = 0
    while start < len(data):
        newline = data.find(b"\n", start)
        end = len(data) if newline < 0 else newline
        if end - start > MAX_LINE_BYTES and not found_line_too_long:
            diagnostics.append(
                _diagnostic(
                    path,
                    "profile-structure",
                    "line-too-long",
                    f"normalized line exceeds {MAX_LINE_BYTES} bytes",
                    line,
                )
            )
            found_line_too_long = True
        if line > MAX_INPUT_LINES and not found_line_limit:
            diagnostics.append(
                _diagnostic(
                    path,
                    "profile-structure",
                    "line-limit",
                    f"input exceeds {MAX_INPUT_LINES} normalized lines",
                    line,
                )
            )
            found_line_limit = True
        if newline < 0 or newline + 1 == len(data):
            break
        start = newline + 1
        line += 1
    return deterministic_diagnostics(diagnostics)


def _read_stream(stream: BinaryIO, path: str) -> tuple[bytes | None, Diagnostic | None]:
    buffer = bytearray()
    while len(buffer) <= MAX_INPUT_BYTES:
        request_size = min(READ_CHUNK_BYTES, MAX_INPUT_BYTES + 1 - len(buffer))
        try:
            chunk = stream.read(request_size)
        except (OSError, ValueError) as exc:
            return None, _diagnostic(path, "host-input", "read-failed", str(exc))
        if chunk is None:
            return None, _diagnostic(
                path,
                "host-input",
                "read-boundary",
                "input stream returned no byte boundary",
            )
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            return None, _diagnostic(
                path,
                "host-input",
                "read-boundary",
                "input stream did not return bytes",
            )
        if _byte_length(chunk) > request_size:
            return None, _diagnostic(
                path,
                "host-input",
                "read-boundary",
                "input stream exceeded the requested bounded read",
            )
        if not chunk:
            return bytes(buffer), None
        buffer.extend(chunk)
        if len(buffer) > MAX_INPUT_BYTES:
            return None, _diagnostic(
                path,
                "profile-structure",
                "input-too-large",
                f"input exceeds {MAX_INPUT_BYTES} bytes",
            )
    return bytes(buffer), None


def _source_bytes(
    source: bytes | bytearray | memoryview | str | os.PathLike[str] | BinaryIO,
    path: str | None,
) -> tuple[bytes | None, str, Diagnostic | None]:
    if isinstance(source, (bytes, bytearray, memoryview)):
        label = path or "<input>"
        if _byte_length(source) > MAX_INPUT_BYTES:
            return None, label, _diagnostic(
                label,
                "profile-structure",
                "input-too-large",
                f"input exceeds {MAX_INPUT_BYTES} bytes",
            )
        return bytes(source), label, None

    if isinstance(source, (str, os.PathLike)):
        label = path or str(source)
        try:
            with Path(source).open("rb") as stream:
                data, error = _read_stream(stream, label)
        except OSError as exc:
            return None, label, _diagnostic(label, "host-input", "read-failed", str(exc))
        return data, label, error

    label = path or str(getattr(source, "name", "<input>"))
    if not hasattr(source, "read"):
        return None, label, _diagnostic(
            label,
            "host-input",
            "read-failed",
            "input source is not bytes, a path, or a binary stream",
        )
    data, error = _read_stream(source, label)
    return data, label, error


def normalize_input(data: bytes, path: str = "<input>") -> InputResult:
    """Validate bounded UTF-8 input and return normalized LF text and lines."""
    if len(data) > MAX_INPUT_BYTES:
        diagnostic = _diagnostic(
            path,
            "profile-structure",
            "input-too-large",
            f"input exceeds {MAX_INPUT_BYTES} bytes",
        )
        return InputResult(path, None, diagnostics=(diagnostic,))

    diagnostics: list[Diagnostic] = []
    if data.startswith(UTF8_BOM):
        diagnostics.append(
            _diagnostic(
                path,
                "unsupported-profile-syntax",
                "utf8-bom",
                "UTF-8 BOM is not allowed by the profile",
                1,
            )
        )
    nul = data.find(b"\x00")
    if nul >= 0:
        diagnostics.append(
            _diagnostic(
                path,
                "unsupported-profile-syntax",
                "nul-byte",
                "NUL bytes are not allowed by the profile",
                _line_number(data, nul),
            )
        )
    bare_cr = _first_bare_cr(data)
    if bare_cr is not None:
        diagnostics.append(
            _diagnostic(
                path,
                "unsupported-profile-syntax",
                "bare-cr",
                "bare carriage returns are not allowed by the profile; use LF or CRLF",
                _line_number(data, bare_cr),
            )
        )
    normalized = data.replace(b"\r\n", b"\n")
    diagnostics.extend(_line_limit_diagnostics(normalized, path))

    try:
        text = normalized.decode("utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            _diagnostic(
                path,
                "host-input",
                "invalid-utf8",
                "input is not valid UTF-8",
                _line_number(normalized, exc.start),
            ),
        )

    if diagnostics:
        return InputResult(path, None, diagnostics=deterministic_diagnostics(diagnostics))

    if not text:
        lines = ()
    else:
        lines = tuple(text.split("\n"))
        if text.endswith("\n"):
            lines = lines[:-1]
    return InputResult(path, text, lines)


def read_input(
    source: bytes | bytearray | memoryview | str | os.PathLike[str] | BinaryIO,
    path: str | None = None,
) -> InputResult:
    """Read at most the profile byte bound, then normalize the input."""
    data, label, error = _source_bytes(source, path)
    if error is not None:
        return InputResult(label, None, diagnostics=(error,))
    if data is None:
        return InputResult(
            label,
            None,
            diagnostics=(
                _diagnostic(label, "host-input", "read-failed", "no input data was supplied"),
            ),
        )
    return normalize_input(data, label)
