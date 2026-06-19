from flask import Flask, render_template, request, Response
import json
from compression.huffman import (
    build_frequency_table,
    build_huffman_tree,
    generate_huffman_codes,
    encode_text,
    decode_text,
    calculate_compression_statistics,
    binary_string_to_bytes,
    parse_huff_file
)


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return render_template("results.html", error="No file part found")

    file = request.files["file"]

    if file.filename == "":
        return render_template("results.html", error="No selected file")

    # Read file content
    content = file.read().decode("utf-8", errors="ignore")

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

    # Formatting helpers
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
        binary_file_size=compressed_file_size,
        encoded_text=formatted_encoded_text,
        decoded_text=decoded_text,
        raw_encoded_text=encoded_text,
        raw_frequency_table=frequency_table,
        original_bar_width=original_bar_width,
        encoded_bar_width=encoded_bar_width
    )


@app.route("/decompress", methods=["POST"])
def decompress_file():
    if "file" not in request.files:
        return render_template("results.html", error="No file uploaded")

    file = request.files["file"]

    if file.filename == "":
        return render_template("results.html", error="No file selected")

    content = file.read().decode("utf-8")

    # Parse .huff file
    frequency_table, encoded_text = parse_huff_file(content)

    # Rebuild Huffman tree
    huffman_tree = build_huffman_tree(frequency_table)

    # Decode text
    decoded_text = decode_text(encoded_text, huffman_tree)

    return render_template(
        "results.html",
        decompressed_text=decoded_text
    )


@app.route("/download", methods=["POST"])
def download_file():
    encoded_text = request.form.get("encoded_text")
    frequency_table_raw = request.form.get("frequency_table")

    if not encoded_text or not frequency_table_raw:
        return "Missing data"

    frequency_table = json.loads(frequency_table_raw)

    header = {
        "freq": frequency_table,
        "original_size": len(encoded_text),
        "encoding": "huffman",
        "version": "HUFF1"
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


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)