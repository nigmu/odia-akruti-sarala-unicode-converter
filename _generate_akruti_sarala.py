"""Generate akruti_sarala.py from the HTML converter source.

Why this file exists:
    akruti_sarala.py is generated from the HTML converter so the Python port
    stays in sync when the upstream mapping table or post-processing rules change.
    Regenerate instead of hand-editing the large TEXT_ARRAY in akruti_sarala.py.

What it does:
    Parses TEXT_ARRAY and post-processing logic from
    Converter/Akruti-Sarala - Unicode Converter.htm and writes akruti_sarala.py.

Usage:
    python _generate_akruti_sarala.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "Converter" / "Akruti-Sarala - Unicode Converter.htm"
OUT_PATH = ROOT / "akruti_sarala.py"


def parse_text_array(html: str) -> list[tuple[str, str]]:
    start = html.index("var text_array = new Array(")
    end = html.index("\n)", start)
    block = html[start:end]

    pairs: list[tuple[str, str]] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        code = stripped.split("//", 1)[0].strip().rstrip(",")
        match = re.match(r'"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"', code)
        if not match:
            continue
        src = match.group(1)
        dst = match.group(2)
        # JS "\\" in the HTML source is a single backslash character.
        if src == "\\\\":
            src = "\\"
        pairs.append((src, dst))
    return pairs


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    pairs = parse_text_array(html)

    lines = [
        '"""Akruti Sarala to Unicode Odia converter.',
        "",
        "Ported from Converter/Akruti-Sarala - Unicode Converter.htm",
        "(Manoj Sahukar, Subhashish Panigrahi; CC-BY-SA 3.0).",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import re",
        "",
        "TEXT_ARRAY: list[tuple[str, str]] = [",
    ]
    for src, dst in pairs:
        lines.append(f"    ({src!r}, {dst!r}),")
    lines.extend(
        [
            "]",
            "",
            "_CONSONANTS = r\"[କଖଗଘଙଚଛଜଝଞଟଠଡଡ଼ଢଢ଼ଣତଥଦଧନପଫବଭମଯୟରଲବୱଶଷସହକ୍ଷଡ଼ଳ]\"",
            "_CONSONANTS_HAL = r\"[କଖଗଘଚଛଜଝଟଠଡଡ଼ଢଢ଼ଣତଥନପଫବଭମୟରଲବୱଶଷସହକ୍ଷଡ଼ଳ]\"",
            "_CONSONANTS_REPH = r\"[କଖଗଘଚଛଜଝଟଠଡଡ଼ଢଢ଼ଣତଥଦଧନପଫବଭମଯରଲଳଵଶଷସହକ୍ଷଜ୍ଞୟ]\"",
            "_MATRAS = r\"[ାିୀୁୂୃେୈୋୌଂଁ]\"",
            "",
            "",
            "def _replace_symbols(text: str) -> str:",
            '    """Apply sequential symbol replacements from the original converter."""',
            "    result = text",
            "    for src, dst in TEXT_ARRAY:",
            "        while src in result:",
            "            result = result.replace(src, dst)",
            "    return result",
            "",
            "",
            "def _post_process(text: str) -> str:",
            '    """Adjust matra, reph, and anusvara positions (Replace_text post-processing)."""',
            "    result = text",
            "",
            "    result = re.sub(",
            '        rf"([ù])({_CONSONANTS})",',
            '        r"\\2\\1",',
            "        result,",
            "    )",
            "    result = re.sub(",
            '        rf"([ù])([୍])({_CONSONANTS_HAL})",',
            '        r"\\2\\3\\1",',
            "        result,",
            "    )",
            "    result = re.sub(",
            '        rf"([ù])([୍])({_CONSONANTS_HAL})",',
            '        r"\\2\\3\\1",',
            "        result,",
            "    )",
            "",
            '    result = result.replace("ùø", "ୌ")',
            '    result = result.replace("ùା", "ୋ")',
            '    result = result.replace("ù÷", "ୈ")',
            '    result = result.replace("ù", "େ")',
            "",
            "    result = re.sub(",
            '        rf"({_CONSONANTS_REPH})({_MATRAS}*)à",',
            '        r"ð\\1\\2",',
            "        result,",
            "    )",
            "    result = re.sub(",
            '        rf"({_CONSONANTS_REPH})({_MATRAS}*)ð",',
            '        r"ð\\1\\2",',
            "        result,",
            "    )",
            "    result = re.sub(",
            '        rf"({_CONSONANTS_REPH})([୍])à",',
            '        r"ð\\1\\2",',
            "        result,",
            "    )",
            "    result = re.sub(",
            '        rf"({_CONSONANTS_REPH})([୍])ð",',
            '        r"ð\\1\\2",',
            "        result,",
            "    )",
            '    result = result.replace("ð", "ର୍")',
            "",
            "    result = re.sub(",
            '        rf"([ଂଁ])({_MATRAS})",',
            '        r"\\2\\1",',
            "        result,",
            "    )",
            "",
            "    return result",
            "",
            "",
            "def convert_to_unicode(text: str) -> str:",
            '    """Convert Akruti Sarala encoded text to Unicode Odia."""',
            "    if not text:",
            "        return text",
            "    modified = _replace_symbols(text)",
            "    return _post_process(modified)",
            "",
        ]
    )

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(pairs)} replacement pairs)")


if __name__ == "__main__":
    main()
