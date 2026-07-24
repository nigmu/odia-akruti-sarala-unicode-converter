"""Orchestrate Akruti Sarala document conversion: extract, convert, write DOCX.

Why this file exists:
    The pipeline ties together extract.py, akruti_sarala.py, and write_docx.py
    so PDF/DOCX inputs can be batch-processed from /input to
    /output without calling each step manually.

What it does:
    Reads files from /input (or a path you pass on the command line),
    extracts text, converts Akruti Sarala to Unicode Odia, and writes DOCX files
    to /output with a _unicode suffix.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from akruti_sarala import convert_to_unicode
from extract import SUPPORTED_EXTENSIONS, UnsupportedFormatError, extract_text
from write_docx import write_docx

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"


def output_path_for(input_path: Path, output_dir: Path = OUTPUT_DIR) -> Path:
    return output_dir / f"{input_path.stem}_unicode.docx"


def process_file(
    input_path: Path,
    output_dir: Path = OUTPUT_DIR,
    *,
    verbose: bool = True,
) -> Path:
    """Extract, convert, and write one input file. Returns the output path."""
    raw_text = extract_text(input_path)
    unicode_text = convert_to_unicode(raw_text)
    out_path = output_path_for(input_path, output_dir)
    write_docx(unicode_text, out_path)

    if verbose:
        print(f"Converted: {input_path.name} -> {out_path.name}")

    return out_path


def process_directory(
    input_dir: Path = INPUT_DIR,
    output_dir: Path = OUTPUT_DIR,
    *,
    verbose: bool = True,
) -> list[Path]:
    """Process all supported files in input_dir. Returns list of output paths."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    inputs = sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not inputs:
        if verbose:
            print(f"No PDF or DOCX files found in {input_dir}")
        return outputs

    for input_path in inputs:
        try:
            outputs.append(process_file(input_path, output_dir, verbose=verbose))
        except (UnsupportedFormatError, FileNotFoundError, OSError) as exc:
            print(f"Skipped {input_path.name}: {exc}", file=sys.stderr)

    return outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Akruti Sarala PDF/DOCX files to Unicode Odia DOCX."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional file paths to convert. If omitted, processes /input/.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR.relative_to(ROOT)})",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    verbose = not args.quiet
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.paths:
        exit_code = 0
        for path_str in args.paths:
            input_path = Path(path_str)
            try:
                process_file(input_path, args.output_dir, verbose=verbose)
            except (UnsupportedFormatError, FileNotFoundError, OSError) as exc:
                print(f"Error processing {input_path}: {exc}", file=sys.stderr)
                exit_code = 1
        return exit_code

    process_directory(INPUT_DIR, args.output_dir, verbose=verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
