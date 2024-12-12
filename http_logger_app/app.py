import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Environment variables to control functionality
LOG_HEADERS = os.getenv("LOG_HEADERS", "true").lower() == "true"
LOG_CONTENT = os.getenv("LOG_CONTENT", "true").lower() == "true"
LOG_SIZE = os.getenv("LOG_SIZE", "true").lower() == "true"

UPLOAD_FORM = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Upload</title>
</head>
<body>
    <h1>Upload a File</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
</body>
</html>
"""

UPLOAD_RESULT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Result</title>
</head>
<body>
    <h1>File Uploaded Successfully</h1>
    <p><strong>Filename:</strong> {{ filename }}</p>
    <p><strong>File Size:</strong> {{ file_size }} bytes</p>
    <a href="/upload">Upload Another File</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def log_request():
    response = {}

    if LOG_HEADERS:
        headers = {header: value for header, value in request.headers}
        response["headers"] = headers
        print("\n--- Headers ---")
        for header, value in headers.items():
            print(f"{header}: {value}")

    if LOG_CONTENT:
        content = request.get_data(as_text=True)
        response["content"] = content
        print("\n--- Content ---")
        print(content)

    if LOG_SIZE:
        size = len(request.get_data())
        response["size"] = size
        print("\n--- Size ---")
        print(f"Request size: {size} bytes")

    return response, 200

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    upload_directory = "files"

    # Create directory if it doesn't exist
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    if request.method == 'GET':
        return render_template_string(UPLOAD_FORM)
    elif request.method == 'POST':
        file = request.files.get('file')
        if file:
            file_path = os.path.join(upload_directory, file.filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            return render_template_string(UPLOAD_RESULT_TEMPLATE, filename=file.filename, file_size=file_size)
        return render_template_string("<p>No file uploaded. <a href='/upload'>Try again.</a></p>")

if __name__ == "__main__":
    # Host and port can also be configured via environment variables
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 5000))
    app.run(host=host, port=port)