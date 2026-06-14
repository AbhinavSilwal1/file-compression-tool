from flask import Flask, render_template, request

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

    return f"""
    <h2>File Uploaded Successfully</h2>
    <p><b>Filename:</b> {file.filename}</p>
    <p><b>Size:</b> {len(content)} characters</p>
    <a href="/">Go Back</a>
    """

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)