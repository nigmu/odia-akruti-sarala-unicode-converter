import subprocess
import sys

from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

ROOT_DIR = Path(__file__).resolve().parent

INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def clear_directory(directory: Path):
    for file in directory.iterdir():
        if not file.is_file():
            continue

        if file.name == ".gitkeep":
            continue

        try:
            file.unlink()
        except Exception:
            pass

@app.route("/")
def index():
    return send_file(ROOT_DIR / "index.html")


@app.route("/upload", methods=["POST"])
def upload():

    # Remove previous conversion files
    clear_directory(INPUT_DIR)
    clear_directory(OUTPUT_DIR)

    file = request.files.get("file")

    if file is None:
        return jsonify(
            success=False,
            message="No file uploaded."
        ), 400

    if file.filename == "":
        return jsonify(
            success=False,
            message="No file selected."
        ), 400

    extension = Path(file.filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        return jsonify(
            success=False,
            message="Only PDF and DOCX files are supported."
        ), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = secure_filename(f"{timestamp}{extension}")

    input_path = INPUT_DIR / filename
    file.save(input_path)

    try:

        subprocess.run(
            [
                sys.executable,
                "pipeline.py",
                str(input_path)
            ],
            check=True
        )

    except subprocess.CalledProcessError:

        if input_path.exists():
            input_path.unlink()

        return jsonify(
            success=False,
            message="Pipeline execution failed."
        ), 500

    output_filename = f"{input_path.stem}_unicode.docx"
    output_path = OUTPUT_DIR / output_filename

    if not output_path.exists():

        if input_path.exists():
            input_path.unlink()

        return jsonify(
            success=False,
            message="Output file was not generated."
        ), 500

    return jsonify(
        success=True,
        filename=output_filename,
        download_url=f"/download/{output_filename}"
    )


@app.route("/download/<filename>")
def download(filename):

    output_path = OUTPUT_DIR / filename

    if not output_path.exists():
        return "File not found.", 404

    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


if __name__ == "__main__":
    # app.run(debug=True)
    # app.run(host="0.0.0.0", port=2004, debug=True)
    app.run(host="0.0.0.0", port=2004, debug=False)