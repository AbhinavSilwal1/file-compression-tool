# File Compression Tool

Web-based file compression tool built with Python and Flask, featuring Huffman Coding for lossless file compression and decompression through a custom `.huff` file format.

## 🚀 Features
- Upload and compress text-based files
- Decompress previously compressed `.huff` files
- Supports multiple file formats:
  - `.txt`
  - `.md`
  - `.json`
  - `.csv`
  - `.log`
- Huffman Coding implementation from scratch
- Automatic frequency table generation
- Huffman tree construction
- Huffman code generation
- Binary encoding and decoding
- Custom `.huff` file format with metadata
- File integrity verification using SHA-256 hashing
- Compression statistics dashboard:
  - Original size
  - Compressed size
  - Compression ratio
  - Compression reduction
  - Space saved
  - Binary file size
- Interactive compression visualization
- Expandable data sections:
  - Frequency Table
  - Huffman Codes
  - Encoded Text
  - Decoded Text
- Download compressed files
- Restore original text files
- File validation and error handling
- Clean and responsive user interface

## 🧠 Purpose
This project is built to strengthen understanding of data compression algorithms while applying them in a complete web application.

It focuses on:
- Huffman Coding
- Data Structures
- File Compression
- Binary Encoding
- File I/O
- Flask Web Development

## 🛠 Technologies Used
- Python
- Flask
- HTML
- CSS

## 📦 How To Run
Clone the repository:
```bash
git clone https://github.com/AbhinavSilwal1/file-compression-tool.git
cd file-compression-tool
```

Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
python3 app.py
```

Open your browser and visit:
```bash
http://127.0.0.1:8000
```