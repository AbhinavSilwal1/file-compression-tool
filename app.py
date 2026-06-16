from flask import Flask, render_template, request, Response
from compression.huffman import (
    build_frequency_table,
    build_huffman_tree,
    generate_huffman_codes,
    encode_text,
    calculate_compression_statistics,
    binary_string_to_bytes
)


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part found"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    # Read file content
    content = file.read().decode("utf-8", errors="ignore")

    # Huffman pipeline
    frequency_table = build_frequency_table(content)
    huffman_tree = build_huffman_tree(frequency_table)
    huffman_codes = generate_huffman_codes(huffman_tree)
    encoded_text = encode_text(content, huffman_codes)
    statistics = calculate_compression_statistics(content, encoded_text)
    binary_data = binary_string_to_bytes(encoded_text)
    compressed_file_size = len(binary_data)

    # Formatting helpers
    def format_binary_string(binary_string, chunk_size=8):
        return ' '.join(binary_string[i:i + chunk_size] for i in range(0, len(binary_string), chunk_size))

    def format_dict(d):
        return '\n'.join(f"{key} : {value}" for key, value in d.items())

    # Formatted display versions
    formatted_frequency_table = format_dict(frequency_table)
    formatted_huffman_codes = format_dict(huffman_codes)
    formatted_encoded_text = format_binary_string(encoded_text)

    return f"""
    <h2>File Uploaded Successfully</h2>

    <p><b>Filename:</b> {file.filename}</p>
    <p><b>Total Characters:</b> {len(content)}</p>
    <p><b>Unique Characters:</b> {len(frequency_table)}</p>
    <p><b>Root Frequency:</b> {huffman_tree.frequency}</p>

    <h3>Frequency Table</h3>
    <pre>{formatted_frequency_table}</pre>

    <h3>Huffman Codes</h3>
    <pre>{formatted_huffman_codes}</pre>

    <h3>Compression Statistics</h3>
    <p><b>Original Size:</b> {statistics["original_size"]} bits</p>
    <p><b>Encoded Size:</b> {statistics["encoded_size"]} bits</p>
    <p><b>Compression Reduction:</b> {statistics["compression_reduction"]:.2f}%</p>
    <p><b>Binary File Size:</b> {compressed_file_size} bytes</p>

    <h3>Encoded Text</h3>
    <pre>{formatted_encoded_text}</pre>

    <form action="/download" method="POST">
        <input type="hidden" name="encoded_text" value="{encoded_text}">
        <button type="submit">Download Compressed File (.bin)</button>
    </form>

    <a href="/">Go Back</a>
    """


@app.route("/download", methods=["POST"])
def download_file():
    encoded_text = request.form.get("encoded_text")

    if not encoded_text:
        return "No encoded data found"

    binary_data = binary_string_to_bytes(encoded_text)

    return Response(
        binary_data,
        mimetype="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=compressed.bin"
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)