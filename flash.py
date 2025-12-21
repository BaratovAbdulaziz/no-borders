#!/usr/bin/env python3
"""
Flash Drive File Server with Auto Setup
Creates venv, installs deps, and serves files from flash drive
"""

import os
import sys
import subprocess
import platform
import socket

# Configuration
VENV_NAME = "fileserver_venv"
PORT = 8000
REQUIREMENTS = ["flask", "flask-cors"]

def get_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def create_venv():
    """Create virtual environment"""
    print(f"[*] Creating virtual environment: {VENV_NAME}")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_NAME])
    print("[+] Virtual environment created")

def get_venv_python():
    """Get path to venv python executable"""
    if platform.system() == "Windows":
        return os.path.join(VENV_NAME, "Scripts", "python.exe")
    return os.path.join(VENV_NAME, "bin", "python")

def get_venv_pip():
    """Get path to venv pip executable"""
    if platform.system() == "Windows":
        return os.path.join(VENV_NAME, "Scripts", "pip.exe")
    return os.path.join(VENV_NAME, "bin", "pip")

def install_deps():
    """Install required packages in venv"""
    print("[*] Installing dependencies...")
    pip_path = get_venv_pip()
    for pkg in REQUIREMENTS:
        print(f"  - Installing {pkg}")
        subprocess.check_call([pip_path, "install", pkg, "-q"])
    print("[+] Dependencies installed")

def detect_flash_drive():
    """Detect flash drive path"""
    system = platform.system()
    
    if system == "Windows":
        import string
        from ctypes import windll
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        drive_type = windll.kernel32.GetDriveTypeW(drive)
                        if drive_type == 2:  # Removable drive
                            drives.append(drive)
                    except:
                        pass
            bitmask >>= 1
        return drives
    
    elif system == "Linux":
        media_paths = ["/media", "/mnt"]
        drives = []
        for base in media_paths:
            if os.path.exists(base):
                for item in os.listdir(base):
                    path = os.path.join(base, item)
                    if os.path.ismount(path):
                        drives.append(path)
        return drives
    
    elif system == "Darwin":  # macOS
        volumes = "/Volumes"
        drives = []
        if os.path.exists(volumes):
            for item in os.listdir(volumes):
                path = os.path.join(volumes, item)
                if os.path.ismount(path) and item != "Macintosh HD":
                    drives.append(path)
        return drives
    
    return []

def create_server_script(drive_path):
    """Create the Flask server script"""
    server_code = f'''
from flask import Flask, send_from_directory, render_template_string, abort
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DRIVE_PATH = r"{drive_path}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flash Drive Server</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .file-list {{ list-style: none; padding: 0; }}
        .file-item {{ padding: 10px; margin: 5px 0; background: #f9f9f9; border-radius: 4px; }}
        .file-item a {{ text-decoration: none; color: #0066cc; }}
        .file-item a:hover {{ text-decoration: underline; }}
        .folder {{ color: #ff9800; font-weight: bold; }}
        .file {{ color: #0066cc; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Flash Drive File Browser</h1>
        <div class="breadcrumb">Path: {{{{ path }}}}</div>
        <ul class="file-list">
            {{% if parent %}}
            <li class="file-item">
                <a href="{{{{ parent }}}}" class="folder">📁 .. (Parent Directory)</a>
            </li>
            {{% endif %}}
            {{% for item in items %}}
            <li class="file-item">
                {{% if item.is_dir %}}
                <a href="/browse/{{{{ item.path }}}}" class="folder">📁 {{{{ item.name }}}}</a>
                {{% else %}}
                <a href="/download/{{{{ item.path }}}}" class="file">📄 {{{{ item.name }}}}</a>
                {{% endif %}}
            </li>
            {{% endfor %}}
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
            items.append({{
                'name': item,
                'path': rel_path,
                'is_dir': os.path.isdir(item_path)
            }})
    except PermissionError:
        abort(403)
    
    parent = None
    if subpath:
        parent_path = os.path.dirname(subpath)
        parent = f"/browse/{{parent_path}}" if parent_path else "/"
    
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
    print(f"[+] Serving files from: {{DRIVE_PATH}}")
    app.run(host='0.0.0.0', port={PORT}, debug=False)
'''
    
    with open("server.py", "w") as f:
        f.write(server_code)
    print("[+] Server script created: server.py")

def main():
    print("="*60)
    print("Flash Drive File Server - Auto Setup")
    print("="*60)
    
    # Check if venv exists
    if not os.path.exists(VENV_NAME):
        create_venv()
        install_deps()
    else:
        print(f"[*] Virtual environment already exists: {VENV_NAME}")
        if input("Reinstall dependencies? (y/n): ").lower() == 'y':
            install_deps()
    
    # Detect flash drives
    print("\n[*] Detecting flash drives...")
    drives = detect_flash_drive()
    
    if not drives:
        print("[!] No flash drives detected!")
        drive_path = input("Enter flash drive path manually: ").strip()
        if not os.path.exists(drive_path):
            print("[!] Path does not exist!")
            sys.exit(1)
    elif len(drives) == 1:
        drive_path = drives[0]
        print(f"[+] Found flash drive: {drive_path}")
    else:
        print("[+] Multiple drives detected:")
        for i, drive in enumerate(drives, 1):
            print(f"  {i}. {drive}")
        choice = int(input("Select drive number: ")) - 1
        drive_path = drives[choice]
    
    # Create server script
    create_server_script(drive_path)
    
    # Get IP and show access info
    ip = get_ip()
    print("\n" + "="*60)
    print("[+] Setup complete!")
    print(f"[+] Starting server on {ip}:{PORT}")
    print(f"[+] Access from browser: http://{ip}:{PORT}")
    print(f"[+] Local access: http://localhost:{PORT}")
    print("="*60 + "\n")
    
    # Run the server
    venv_python = get_venv_python()
    subprocess.call([venv_python, "server.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Server stopped")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
