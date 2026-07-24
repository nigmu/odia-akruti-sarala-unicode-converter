"""Validate akruti_sarala.py against the original JavaScript converter.

Why this file exists:
    The Python port must produce identical output to the browser converter.
    This script catches regressions after edits to akruti_sarala.py or after
    regenerating it from the HTML source.

What it does:
    Runs the same sample strings through akruti_sarala.convert_to_unicode() and
    the JavaScript convert_to_unicode() from the HTML file (via Node.js), then
    reports any mismatches.

Usage:
    python _validate_akruti.py
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SAMPLES = [
    "K@",
    "@",
    "K",
    "e",
    "Ka",
    "Kû",
    "namaskar",
    "Odia",
    "1",
    "2",
    "3",
    "*",
    "<",
    "{",
    "}",
    "\\",
    "ù",
    "Kù",
    "Kù÷",
    "Kùø",
]

NODE_SCRIPT = ROOT / "_validate_node_runner.js"
HTML = ROOT / "Converter" / "Akruti-Sarala - Unicode Converter.htm"


def js_results(samples: list[str]) -> dict[str, str]:
    js = HTML.read_text(encoding="utf-8")
    start = js.index("<script type=\"text/javascript\">") + len('<script type="text/javascript">')
    end = js.index("</script>", start)
    body = js[start:end]

    runner = f"""
{body}
function convertInput(input) {{
  const fields = {{ nonunicode_text: "", unicode_text: "" }};
  document = {{
    getElementById: (id) => ({{
      get value() {{ return fields[id]; }},
      set value(v) {{ fields[id] = v; }},
    }}),
  }};
  fields.nonunicode_text = input;
  convert_to_unicode();
  return fields.unicode_text;
}}
const samples = {json.dumps(samples, ensure_ascii=False)};
const out = {{}};
for (const s of samples) out[s] = convertInput(s);
process.stdout.write(JSON.stringify(out));
"""
    NODE_SCRIPT.write_text(runner, encoding="utf-8")
    raw = subprocess.check_output(["node", str(NODE_SCRIPT)], encoding="utf-8")
    return json.loads(raw)


def py_results(samples: list[str]) -> dict[str, str]:
    from akruti_sarala import convert_to_unicode

    return {s: convert_to_unicode(s) for s in samples}


def main() -> None:
    js_out = js_results(SAMPLES)
    py_out = py_results(SAMPLES)

    mismatches = [
        {"sample": s, "python": py_out[s], "javascript": js_out[s]}
        for s in SAMPLES
        if py_out[s] != js_out[s]
    ]

    report = ROOT / "_validation_report.json"
    report.write_text(
        json.dumps({"mismatches": mismatches, "total": len(SAMPLES)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if mismatches:
        raise SystemExit(f"FAIL: {len(mismatches)} mismatches (see {report.name})")
    print(f"OK: {len(SAMPLES)} samples matched JS converter.")


if __name__ == "__main__":
    main()
