import sys
import os
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

from flask import Flask, request, jsonify, redirect, url_for, send_file, flash, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import threading
import uuid
import zipfile
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

progress = {}  # task_id -> progress % or -1 for error

def extract_zip(zip_path: Path, extract_to: Path, task_id: str):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        progress[task_id] = 100
    except Exception as e:
        progress[task_id] = -1
        print(f"[{task_id}] Extraction error: {e}")

def background_task(task_id: str, zip_path: Path, extract_path: Path, base_url: str):
    progress[task_id] = 0
    extract_zip(zip_path, extract_path, task_id)
    update_public_json(base_url)

def update_public_json(base_url=None):
    if base_url is None:
        base_url = "http://localhost:5000"
    files_list = []
    for zip_file in sorted(UPLOAD_DIR.glob("*.zip")):
        files_list.append({
            "id": zip_file.name,
            "file_url": f"{base_url}/game/{zip_file.name}",
            "size": zip_file.stat().st_size
        })
    json_path = Path(__file__).parent / "trd_public.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(files_list, f, indent=2)
    print(f"Updated trd_public.json with {len(files_list)} files")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return redirect(url_for("upload_page"))
    
    zipped_files = sorted(f for f in UPLOAD_DIR.glob("*.zip"))
    files = []
    base_url = request.url_root.rstrip("/")
    for f in zipped_files:
        files.append({
            "name": f.name,
            "url": f"{base_url}/game/{f.name}",
            "size_bytes": f.stat().st_size
        })
    return render_template("upload.html", files=files, error=None)

@app.route("/upload_page", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        files = request.files.getlist("files[]")
        if not files or any(not f.filename.lower().endswith(".zip") for f in files):
            flash("Please upload zip files only")
            return redirect(url_for("upload_page"))

        base_url = request.url_root.rstrip("/")
        tasks = []
        for file in files:
            original_name = file.filename
            filename = secure_filename(original_name)
            save_path = UPLOAD_DIR / filename
            file.save(save_path)

            extract_path = UPLOAD_DIR / (filename + "_extracted")
            if extract_path.exists():
                for item in extract_path.rglob("*"):
                    if item.is_file():
                        item.unlink()
                    else:
                        try:
                            item.rmdir()
                        except:
                            pass
                try:
                    extract_path.rmdir()
                except:
                    pass
            extract_path.mkdir(parents=True, exist_ok=True)

            task_id = str(uuid.uuid4())
            threading.Thread(target=background_task, args=(task_id, save_path, extract_path, base_url)).start()

            tasks.append({
                "task_id": task_id,
                "filename": filename,
                "original_name": original_name,
                "download_url": f"{base_url}/game/{filename}"
            })

        return jsonify({"tasks": tasks})

    zipped_files = sorted(f for f in UPLOAD_DIR.glob("*.zip"))
    files = []
    base_url = request.url_root.rstrip("/")
    for f in zipped_files:
        files.append({
            "name": f.name,
            "url": f"{base_url}/game/{f.name}",
            "size_bytes": f.stat().st_size
        })
    return render_template("listing.html", files=files)

@app.route("/progress/<task_id>")
def progress_status(task_id):
    p = progress.get(task_id)
    if p is None:
        return jsonify({"error": "Invalid task ID"}), 404
    return jsonify({"progress": p})

@app.route("/game/<path:filename>")
def serve_file(filename):
    file_path = UPLOAD_DIR / filename
    if file_path.exists() and file_path.is_file():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route("/trd_public.json")
def serve_public_json():
    json_path = Path(__file__).parent / "trd_public.json"
    if json_path.exists():
        return send_file(json_path)
    return "File not found", 404

if __name__ == "__main__":
    print("Starting Flask app on http://0.0.0.0:5000")
    update_public_json()
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=5000)
