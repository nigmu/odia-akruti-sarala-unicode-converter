# Odia Akruti Sarala Unicode Converter

An end-to-end pipeline for converting legacy **Akruti Sarala** encoded Odia documents into editable Unicode DOCX files.

Unlike the original browser-based converter, this project automates the complete workflow:

- Extract text from PDF or DOCX documents
- Convert Akruti Sarala encoded text to Unicode Odia
- Generate a Unicode DOCX with a proper Odia Unicode font

---

# How to Use

## 1. Clone the repository

```bash
git clone https://github.com/nigmu/odia-akruti-sarala-unicode-converter.git
cd odia-akruti-sarala-unicode-converter
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows

```powershell
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```



## 3. Install dependencies

```bash
pip install -r requirements.txt
```



## 4. Place your input file

Copy your PDF or DOCX into the `input/` directory.

```
input/
    document.pdf
```



## 5. Run the pipeline

```bash
python pipeline.py
```

The converted Unicode document will be written to

```
output/document_unicode.docx
```

Alternatively, convert one or more files directly:

```bash
python pipeline.py myfile.pdf
python pipeline.py file1.pdf file2.docx
```

---



# How It Works

The conversion process consists of four stages.

## 1. Text Extraction

The pipeline first determines whether the input file is a PDF or DOCX.

- **PDFs** are read using **PyMuPDF**.
- **DOCX** files are read using **python-docx**, including paragraphs and table contents.

The extracted document is converted into plain text before any character conversion is performed.

---



## 2. Akruti Sarala → Unicode Conversion

The extracted text is then passed to the conversion engine.

Akruti Sarala is a legacy font encoding rather than a Unicode character set. Each byte or character represents a font glyph instead of an actual Odia Unicode code point. As a result, a simple character-by-character replacement is insufficient because many vowel signs, conjuncts, and ligatures are stored in visual order rather than their logical Unicode order.

The conversion process therefore consists of two stages:

### Character Mapping

The converter first performs a sequential replacement using the mapping table ported from the original Odia Wikimedia JavaScript converter.

Each legacy Akruti Sarala symbol is translated into its corresponding Unicode representation. These mappings include:

- Independent vowels
- Consonants
- Vowel signs (matras)
- Halanta forms
- Conjunct consonants
- Ligatures
- Numerals
- Common punctuation and symbols



### Post-processing

After the initial mapping, the intermediate text is corrected to produce valid Unicode Odia.

This stage applies several linguistic rules, including:

- Reordering pre-base vowel signs such as **େ**, **ୈ**, **ୋ**, and **ୌ** to their proper Unicode positions.
- Reconstructing **Reph (ର୍)** by moving it before the correct consonant cluster.
- Correcting the placement of vowel signs following conjunct consonants.
- Adjusting the position of **Anusvara (ଂ)** and **Chandrabindu (ଁ)** where necessary.
- Normalizing special cases inherited from the legacy font encoding.

The result is Unicode text that follows the logical character ordering expected by modern rendering engines, allowing it to display correctly across applications, operating systems, and Unicode-compliant fonts.

---



## 3. DOCX Generation

After conversion, the Unicode text is written into a new Microsoft Word document.

The generated document:

- preserves paragraph boundaries
- writes one paragraph per extracted line
- applies a Unicode Odia font (`Noto Sans Oriya` by default)

The output is saved as

```
<original_filename>_unicode.docx
```

inside the `output/` directory.

---



## 4. Pipeline Orchestration

`pipeline.py` ties everything together.

```
PDF / DOCX
      │
      ▼
extract.py
      │
      ▼
akruti_sarala.py
      │
      ▼
write_docx.py
      │
      ▼
Unicode DOCX
```

The pipeline can either:

- process every supported document inside the `input/` folder
- process files supplied through the command line

---



# Original Project

This repository builds upon the excellent work of the **Odia Wikimedia** community.

Original converter:

[https://github.com/OdiaWikimedia/Converter/tree/master](https://github.com/OdiaWikimedia/Converter/tree/master)

Specifically, the conversion logic is derived from the browser-based **Akruti Sarala – Unicode Converter** developed by **Manoj Sahukar** and **Subhashish Panigrahi**.

This repository ports that conversion logic to Python and extends it with:

- PDF text extraction
- DOCX text extraction
- command-line interface
- automated processing pipeline
- Unicode DOCX generation

The original character mappings and conversion rules remain attributable to the original project.