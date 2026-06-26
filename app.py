from flask import Flask, render_template, request, Response
import json
import os
import hashlib
from compression.huffman import (
    build_frequency_table,
    build_huffman_tree,
    generate_huffman_codes,
    encode_text,
    decode_text,
    calculate_compression_statistics,
    binary_string_to_bytes,
    parse_huff_file,
    build_tree_from_codes
)


app = Flask(__name__)


# --------------------------------
# Home Page
# --------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# Compression
# --------------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return render_template("results.html", error="No file part found")

    file = request.files["file"]

    filename = file.filename.lower()
    _, file_extension = os.path.splitext(filename)

    allowed_types = {".txt", ".md", ".json", ".csv", ".log"}

    if file_extension not in allowed_types:
        return render_template(
            "results.html",
            error=f"Unsupported file type: {file_extension}. Only text-based files are supported (.txt, .md, .json, .csv, .log)"
        )

    if file.filename == "":
        return render_template("results.html", error="No selected file")

    raw_bytes = file.read()

    try:
        content = raw_bytes.decode("utf-8")

        # Generate integrity hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    except UnicodeDecodeError:
        return render_template(
            "results.html",
            error="File is not valid UTF-8 text. Please upload a plain text file."
        )
    
    if not content.strip():
        return render_template("results.html", error="Uploaded file is empty")

    # Huffman pipeline
    frequency_table = build_frequency_table(content)

    if len(frequency_table) == 0:
        return render_template("results.html", error="No valid characters to compress")

    huffman_tree = build_huffman_tree(frequency_table)
    huffman_codes = generate_huffman_codes(huffman_tree)
    encoded_text = encode_text(content, huffman_codes)
    decoded_text = decode_text(encoded_text, huffman_tree)
    statistics = calculate_compression_statistics(content, encoded_text)
    binary_data = binary_string_to_bytes(encoded_text)
    compressed_file_size = len(binary_data)

    original_size = statistics["original_size"]
    encoded_size = statistics["encoded_size"]

    max_bar_width = 300
    original_bar_width = max_bar_width
    encoded_bar_width = int((encoded_size / original_size) * max_bar_width)

    # Display formatting helpers
    def format_binary_string(binary_string, chunk_size=8):
        return ' '.join(binary_string[i:i + chunk_size] for i in range(0, len(binary_string), chunk_size))

    def format_dict(d):
        lines = []

        for key, value in d.items():
            if key == " ":
                display_key = "[SPACE]"
            elif key == "\n":
                display_key = "[NEWLINE]"
            elif key == "\t":
                display_key = "[TAB]"
            else:
                display_key = key

            lines.append(f"{display_key} : {value}")

        return '\n'.join(lines)

    # Formatted display versions
    formatted_frequency_table = format_dict(frequency_table)
    formatted_huffman_codes = format_dict(huffman_codes)
    formatted_encoded_text = format_binary_string(encoded_text)

    return render_template(
        "results.html",
        filename=file.filename,
        total_characters=len(content),
        unique_characters=len(frequency_table),
        root_frequency=huffman_tree.frequency,
        frequency_table=formatted_frequency_table,
        huffman_codes=formatted_huffman_codes,
        original_size=statistics["original_size"],
        encoded_size=statistics["encoded_size"],
        compression_reduction=f"{statistics['compression_reduction']:.2f}",
        space_saved=statistics["space_saved"],
        compression_ratio=f"{statistics['compression_ratio']:.2f}",
        binary_file_size=compressed_file_size,
        encoded_text=formatted_encoded_text,
        decoded_text=decoded_text,
        raw_encoded_text=encoded_text,
        raw_frequency_table=frequency_table,
        raw_huffman_codes=huffman_codes,
        original_bar_width=original_bar_width,
        encoded_bar_width=encoded_bar_width,
        content_hash=content_hash
    )


# --------------------------------
# Decompression
# --------------------------------
@app.route("/decompress", methods=["POST"])
def decompress_file():
    if "file" not in request.files:
        return render_template("results.html", error="No file uploaded")

    file = request.files["file"]

    if file.filename == "":
        return render_template("results.html", error="No file selected")

    content = file.read().decode("utf-8")

    try:
        # Parse .huff file
        frequency_table, huffman_codes, encoded_text, header = parse_huff_file(content)
        original_hash = header.get("hash")

        # Rebuild Huffman tree
        huffman_tree = build_tree_from_codes(huffman_codes)

        # Decode text
        decoded_text = decode_text(encoded_text, huffman_tree)
        
        # Integrity check
        calculated_hash = hashlib.sha256(decoded_text.encode("utf-8")).hexdigest()

        if original_hash and calculated_hash != original_hash:
            return render_template(
                "results.html",
                error="File integrity check failed. The file may be corrupted or modified."
            )

        return render_template(
            "results.html",
            decompressed_text=decoded_text,
            file_version=header["version"],
            encoding_type=header["encoding"],
            original_filename=header.get("original_filename"),
            file_hash=original_hash
        )
    
    except Exception as error:
        return render_template(
            "results.html",
            error=str(error)
        )


# --------------------------------
# Download Compressed File
# --------------------------------
@app.route("/download", methods=["POST"])
def download_file():
    encoded_text = request.form.get("encoded_text")
    frequency_table_raw = request.form.get("frequency_table")
    original_filename = request.form.get("original_filename")
    huffman_codes_raw = request.form.get("huffman_codes")

    if not encoded_text or not frequency_table_raw:
        return "Missing data"

    frequency_table = json.loads(frequency_table_raw)
    huffman_codes = json.loads(huffman_codes_raw)

    header = {
        "freq": frequency_table,
        "codes": huffman_codes,
        "hash": request.form.get("content_hash"),
        "original_size": len(encoded_text),
        "encoding": "huffman",
        "version": "HUFF1",
        "original_filename": original_filename
    }

    huff_content = (
        "HUFF1\n"
        + json.dumps(header)
        + "\n---\n"
        + encoded_text
    )

    return Response(
        huff_content,
        mimetype="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=compressed.huff"
        }
    )


# --------------------------------
# Download Restored File
# --------------------------------
@app.route("/download-restored", methods=["POST"])
def download_restored():
    restored_text = request.form.get("restored_text")
    original_filename = request.form.get(
        "original_filename",
        "restored.txt"
    )

    if restored_text is None:
        return "Missing restored data"

    return Response(
        restored_text,
        mimetype="text/plain",
        headers={
            "Content-Disposition":
                f"attachment; filename={original_filename}"
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)