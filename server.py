
from flask import Flask, send_from_directory, render_template_string, abort
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DRIVE_PATH = r"/media/k/We need you/"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flash Drive Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .file-list { list-style: none; padding: 0; }
        .file-item { padding: 10px; margin: 5px 0; background: #f9f9f9; border-radius: 4px; }
        .file-item a { text-decoration: none; color: #0066cc; }
        .file-item a:hover { text-decoration: underline; }
        .folder { color: #ff9800; font-weight: bold; }
        .file { color: #0066cc; }
        .breadcrumb { margin-bottom: 20px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Flash Drive File Browser</h1>
        <div class="breadcrumb">Path: {{ path }}</div>
        <ul class="file-list">
            {% if parent %}
            <li class="file-item">
                <a href="{{ parent }}" class="folder">📁 .. (Parent Directory)</a>
            </li>
            {% endif %}
            {% for item in items %}
            <li class="file-item">
                {% if item.is_dir %}
                <a href="/browse/{{ item.path }}" class="folder">📁 {{ item.name }}</a>
                {% else %}
                <a href="/download/{{ item.path }}" class="file">📄 {{ item.name }}</a>
                {% endif %}
            </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return browse("")

@app.route('/browse/')
@app.route('/browse/<path:subpath>')
def browse(subpath=""):
    full_path = os.path.join(DRIVE_PATH, subpath)
    
    if not os.path.exists(full_path):
        abort(404)
    
    if not os.path.isdir(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))
    
    items = []
    try:
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            rel_path = os.path.relpath(item_path, DRIVE_PATH).replace(os.sep, '/')
            items.append({
                'name': item,
                'path': rel_path,
                'is_dir': os.path.isdir(item_path)
            })
    except PermissionError:
        abort(403)
    
    parent = None
    if subpath:
        parent_path = os.path.dirname(subpath)
        parent = f"/browse/{parent_path}" if parent_path else "/"
    
    return render_template_string(HTML_TEMPLATE, 
                                 items=items, 
                                 path=subpath or "/",
                                 parent=parent)

@app.route('/download/<path:filepath>')
def download(filepath):
    full_path = os.path.join(DRIVE_PATH, filepath)
    if not os.path.exists(full_path) or os.path.isdir(full_path):
        abort(404)
    return send_from_directory(os.path.dirname(full_path), 
                             os.path.basename(full_path),
                             as_attachment=True)

if __name__ == '__main__':
    print(f"[+] Serving files from: {DRIVE_PATH}")
    app.run(host='0.0.0.0', port=8000, debug=False)
