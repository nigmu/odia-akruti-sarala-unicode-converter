"""Akruti Sarala to Unicode Odia converter.

Why this file exists:
    The document pipeline (pipeline.py) needs to convert legacy Akruti Sarala
    encoded text extracted from PDF/DOCX files. The original converter lives in
    the browser as JavaScript; this module ports that logic to Python so it can
    run from the command line without a browser.

What it does:
    Applies the same symbol replacements and post-processing rules as
    Converter/Akruti-Sarala - Unicode Converter.htm, exposing convert_to_unicode()
    as the main entry point for the pipeline.

Ported from Converter/Akruti-Sarala - Unicode Converter.htm
(Manoj Sahukar, Subhashish Panigrahi; CC-BY-SA 3.0).
"""

from __future__ import annotations

import re

TEXT_ARRAY: list[tuple[str, str]] = [
    (' û', ' ।'),
    ('ö', ' ।'),
    ('÷÷÷', ''),
    ('£', '୍ମ'),
    ('à', '୍ମ'),
    ('á', '୍ମୃ'),
    ('â', '୍ର'),
    ('ã', '୍ର'),
    ('ä', '୍ଲ'),
    ('å', '୍ଭ'),
    ('æ', '୍ଳ'),
    ('ç', '୍ୱ'),
    ('è', '୍ସ'),
    ('ý', '୍ୟ'),
    ('¥', '୍ୟ'),
    ('ó', 'ିଁ'),
    ('Iß', 'ୱ'),
    ('Wÿ', 'ଡ଼'),
    ('Xÿ', 'ଢ଼'),
    ('Pÿ', 'ଚ'),
    ('[ô', 'ଥି'),
    (']ô', 'ଧି'),
    ('Lô', 'ଖି'),
    ('cô', 'ତ୍ମ'),
    ('_ô', 'ତ୍ପ'),
    ('û', 'ା'),
    ('ò', 'ି'),
    ('ú', 'ୀ'),
    ('ê', 'ୁ'),
    ('ë', 'ୁ'),
    ('ì', 'ୂ'),
    ('í', 'ୂ'),
    ('é', 'ୃ'),
    ('ñ', 'ଁ'),
    ('õ', 'ଂ'),
    ('ü', 'ଃ'),
    ('þ', '୍'),
    ('¨', '୍\u200c'),
    ('1', '୧'),
    ('2', '୨'),
    ('3', '୩'),
    ('4', '୪'),
    ('5', '୫'),
    ('6', '୬'),
    ('7', '୭'),
    ('8', '୮'),
    ('9', '୯'),
    ('0', '୦'),
    ('#', '୰'),
    ('$', 'ଽ'),
    ('&', 'ଌ'),
    ('*', 'ଞ୍ଚ'),
    ('\x81', 'ଞ୍ଚ'),
    ('î', '୍ରୁ'),
    ('ï', '୍ରୂ'),
    ('Ð', 'କ୍ଷ୍ଣ'),
    ('Ñ', '୍କ'),
    ('Ò', '୍ଖ'),
    ('Ó', '୍ଗ'),
    ('Ô', '୍ଚ'),
    ('Õ', '୍ଜ'),
    ('Ö', '୍ଟ'),
    ('×', '୍ଠ'),
    ('Ø', '୍ଡ'),
    ('Ù', '୍ଣ'),
    ('Ú', '୍ଥ'),
    ('Û', '୍ଧ'),
    ('Ü', '୍ନ'),
    ('Ý', '୍ପ'),
    ('Þ', '୍ଫ'),
    ('ß', '୍ୱ'),
    ('<', 'ଣ୍ଟ'),
    ('\x8d', 'ଣ୍ଟ'),
    ('…', 'ଟ୍ଟ'),
    ('μ', 'ମ୍ପ'),
    ('µ', 'ମ୍ପ'),
    ('¶', 'ମ୍ଫ'),
    ('‰', 'ଣ୍ଣ'),
    ('Š', 'ଣ୍ଡ'),
    ('Œ', 'ଣ୍ଠ'),
    ('™', 'ତ୍ମ'),
    ('š', 'ତ୍ପ'),
    ('›', 'ତ୍ସ'),
    ('œ', 'ତ୍ସ୍ନ'),
    ('Ÿ', 'ଦ୍ଦ'),
    ('{', 'ଜ୍ଜ'),
    ('|', 'ଜ୍ଝ'),
    ('}', 'କ୍ର'),
    ('¡', 'ଦ୍ଧ'),
    ('¢', 'ଦ୍ଘ'),
    ('¤', 'ଧ୍ୟ'),
    ('¦', 'ନ୍ଦ'),
    ('§', 'ନ୍ଧ'),
    ('©', 'ତ୍ତ'),
    ('\x8f', 'ତ୍ତ'),
    ('ª', 'ନ୍ତ୍ର'),
    ('«', 'ନ୍ତ'),
    ('¬', 'ଞ୍ଜ'),
    ('ƒ', 'ଞ୍ଝ'),
    ('®', 'ପ୍ପ'),
    ('¯', 'ପ୍ତ'),
    ('°', 'ପ୍ସ'),
    ('±', 'ବ୍ଦ'),
    ('²', 'ବ୍ଧ'),
    ('´', 'ମ୍ବ'),
    ('¸', 'ମ୍ଭ'),
    (' ̧', 'ମ୍ଭ'),
    ('̧', 'ମ୍ଭ'),
    ('¹', 'ମ୍ମ'),
    ('º', 'ଲ୍କ'),
    ('»', 'ଲ୍ଗ'),
    ('¼', 'ଶ୍ଛ'),
    ('½', 'ଶ୍ଚ'),
    ('¾', 'ଷ୍ଣ'),
    ('¿', 'ଷ୍ପ'),
    ('À', 'ଷ୍ଫ'),
    ('Á', 'ଷ୍ଟ'),
    ('Â', 'ଷ୍ଠ'),
    ('Ã', 'ଷ୍କ'),
    ('Ä', 'ସ୍କ'),
    ('Å', 'ସ୍ଖ'),
    ('Æ', 'ସ୍ପ'),
    ('Ç', 'ସ୍ଫ'),
    ('È', 'ସ୍ତ୍ର'),
    ('É', 'ସ୍ତ'),
    ('Ê', 'ସ୍ୱ'),
    ('Ë', 'ଳ୍କ'),
    ('Ì', 'ଳ୍ପ'),
    ('Í', 'ଳ୍ଫ'),
    ('Î', 'ତ୍ଥ'),
    ('\x9d', 'ତ୍ଥ'),
    ('Ï', 'ଳ୍ଳ'),
    ('@ା', 'ଆ'),
    ('@', 'ଅ'),
    ('A', 'ଇ'),
    ('B', 'ଈ'),
    ('C', 'ଉ'),
    ('D', 'ଊ'),
    ('E', 'ଋ'),
    ('F', 'ୠ'),
    ('G', 'ଏ'),
    ('H', 'ଐ'),
    ('I', 'ଓ'),
    ('J', 'ଔ'),
    ('K', 'କ'),
    ('L', 'ଖ'),
    ('M', 'ଗ'),
    ('N', 'ଘ'),
    ('O', 'ଙ'),
    ('P', 'ଚ'),
    ('Q', 'ଛ'),
    ('R', 'ଜ'),
    ('S', 'ଝ'),
    ('T', 'ଞ'),
    ('U', 'ଟ'),
    ('V', 'ଠ'),
    ('W', 'ଡ'),
    ('X', 'ଢ'),
    ('Y', 'ଣ'),
    ('Z', 'ତ'),
    ('[', 'ଥ'),
    ('\\', 'ଦ'),
    (']', 'ଧ'),
    ('^', 'ନ'),
    ('~', 'ଯ'),
    ('_', 'ପ'),
    ('`', 'ଫ'),
    ('a', 'ବ'),
    ('b', 'ଭ'),
    ('c', 'ମ'),
    ('d', 'ୟ'),
    ('e', 'ର'),
    ('f', 'ଲ'),
    ('g', 'ଶ'),
    ('h', 'ଷ'),
    ('i', 'ସ'),
    ('j', 'ହ'),
    ('k', 'ଳ'),
    ('l', 'କ୍ଷ'),
    ('m', 'ଜ୍ଞ'),
    ('n', 'ଦ୍ଭ'),
    ('o', 'କ୍ଟ'),
    ('p', 'କ୍ଟ୍ର'),
    ('q', 'କ୍ତ'),
    ('r', 'କ୍ସ'),
    ('s', 'ଗ୍ଦ'),
    ('t', 'ଗ୍ଧ'),
    ('u', 'ଙ୍କ'),
    ('v', 'ଙ୍ଖ'),
    ('w', 'ଙ୍ଗ'),
    ('x', 'ଙ୍ଘ'),
    ('y', 'ଚ୍ଚ'),
    ('z', 'ଚ୍ଛ'),
    (' ̄', 'ପ୍ତ'),
    (' ́', 'ମ୍ବ'),
    ('‹', 'ଣ୍ଢ'),
    ('ଏø', ' ଐ'),
    ('୍ଯ', '୍ୟ'),
    (' ̈', '୍\u200d'),
    ('ଅା', 'ଆ'),
]

_CONSONANTS = r"[କଖଗଘଙଚଛଜଝଞଟଠଡଡ଼ଢଢ଼ଣତଥଦଧନପଫବଭମଯୟରଲବୱଶଷସହକ୍ଷଡ଼ଳ]"
_CONSONANTS_HAL = r"[କଖଗଘଚଛଜଝଟଠଡଡ଼ଢଢ଼ଣତଥନପଫବଭମୟରଲବୱଶଷସହକ୍ଷଡ଼ଳ]"
_CONSONANTS_REPH = r"[କଖଗଘଚଛଜଝଟଠଡଡ଼ଢଢ଼ଣତଥଦଧନପଫବଭମଯରଲଳଵଶଷସହକ୍ଷଜ୍ଞୟ]"
_MATRAS = r"[ାିୀୁୂୃେୈୋୌଂଁ]"


def _replace_symbols(text: str) -> str:
    """Apply sequential symbol replacements from the original converter."""
    result = text
    for src, dst in TEXT_ARRAY:
        while src in result:
            result = result.replace(src, dst)
    return result


def _post_process(text: str) -> str:
    """Adjust matra, reph, and anusvara positions (Replace_text post-processing)."""
    result = text

    result = re.sub(
        rf"([ù])({_CONSONANTS})",
        r"\2\1",
        result,
    )
    result = re.sub(
        rf"([ù])([୍])({_CONSONANTS_HAL})",
        r"\2\3\1",
        result,
    )
    result = re.sub(
        rf"([ù])([୍])({_CONSONANTS_HAL})",
        r"\2\3\1",
        result,
    )

    result = result.replace("ùø", "ୌ")
    result = result.replace("ùା", "ୋ")
    result = result.replace("ù÷", "ୈ")
    result = result.replace("ù", "େ")

    result = re.sub(
        rf"({_CONSONANTS_REPH})({_MATRAS}*)à",
        r"ð\1\2",
        result,
    )
    result = re.sub(
        rf"({_CONSONANTS_REPH})({_MATRAS}*)ð",
        r"ð\1\2",
        result,
    )
    result = re.sub(
        rf"({_CONSONANTS_REPH})([୍])à",
        r"ð\1\2",
        result,
    )
    result = re.sub(
        rf"({_CONSONANTS_REPH})([୍])ð",
        r"ð\1\2",
        result,
    )
    result = result.replace("ð", "ର୍")

    result = re.sub(
        rf"([ଂଁ])({_MATRAS})",
        r"\2\1",
        result,
    )

    return result


def convert_to_unicode(text: str) -> str:
    """Convert Akruti Sarala encoded text to Unicode Odia."""
    if not text:
        return text
    modified = _replace_symbols(text)
    return _post_process(modified)

