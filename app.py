from flask import Flask, render_template, request
from compression.huffman import build_frequency_table, build_huffman_tree, generate_huffman_codes


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
    frequency_table = build_frequency_table(content)
    huffman_tree = build_huffman_tree(frequency_table)
    huffman_codes = generate_huffman_codes(huffman_tree)

    return f"""
    <h2>File Uploaded Successfully</h2>

    <p><b>Filename:</b> {file.filename}</p>

    <p><b>Total Characters:</b> {len(content)}</p>

    <p><b>Unique Characters:</b> {len(frequency_table)}</p>

    <p><b>Root Frequency:</b> {huffman_tree.frequency}</p>

    <h3>Frequency Table</h3>

    <pre>{frequency_table}</pre>
    
    <h3>Huffman Codes</h3>

    <pre>{huffman_codes}</pre>

    <a href="/">Go Back</a>
    """


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)