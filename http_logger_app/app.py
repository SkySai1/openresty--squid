import os
from flask import Flask, request, render_template_string, send_from_directory

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
    <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" id="fileInput">
        <button type="submit">Upload</button>
    </form>
    <progress id="progressBar" value="0" max="100" style="width: 100%;"></progress>
    <p id="status">Waiting...</p>
    <script>
        const form = document.getElementById('uploadForm');
        const progressBar = document.getElementById('progressBar');
        const status = document.getElementById('status');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.value = percentComplete;
                    status.textContent = `Uploading: ${Math.round(percentComplete)}%`;
                }
            });

            xhr.addEventListener('load', () => {
                status.textContent = 'Upload complete!';
                window.location.href = '/files';
            });

            xhr.addEventListener('error', () => {
                status.textContent = 'Error occurred during upload.';
            });

            xhr.open('POST', '/upload');
            xhr.send(formData);
        });
    </script>
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
    <a href="/files">View Uploaded Files</a>
</body>
</html>
"""

FILES_LIST_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uploaded Files</title>
</head>
<body>
    <h1>Uploaded Files</h1>
    {% if files %}
        <ul>
        {% for file in files %}
            <li><a href="/files/{{ file }}" download>{{ file }}</a></li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No files found.</p>
    {% endif %}
    <a href="/upload">Upload a File</a>
</body>
</html>
"""

CACHE_DIRECTORY = "files"

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
    # Create cache directory if it doesn't exist
    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)

    if request.method == 'GET':
        return render_template_string(UPLOAD_FORM)
    elif request.method == 'POST':
        file = request.files.get('file')
        if file:
            # Save file to cache directory
            file_path = os.path.join(CACHE_DIRECTORY, file.filename)
            file.save(file_path)

            # Calculate file size
            file_size = os.path.getsize(file_path)

            # Return result page
            return render_template_string(UPLOAD_RESULT_TEMPLATE, filename=file.filename, file_size=file_size)

        return render_template_string("<p>No file uploaded. <a href='/upload'>Try again.</a></p>")

@app.route('/files', methods=['GET'])
def list_files():
    # List files in the cache directory
    if os.path.exists(CACHE_DIRECTORY):
        files = os.listdir(CACHE_DIRECTORY)
    else:
        files = []
    return render_template_string(FILES_LIST_TEMPLATE, files=files)

@app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    # Serve files from cache directory
    return send_from_directory(CACHE_DIRECTORY, filename)

if __name__ == "__main__":
    # Host and port can also be configured via environment variables
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 5000))
    app.run(host=host, port=port)
