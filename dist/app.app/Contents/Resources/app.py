from flask import Flask, jsonify, send_file
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.route('/trd_public.json')
def serve_public_json():
    files = []
    base_url = 'http://localhost:5000/files'  # Change if different host/port
    
    for file_path in sorted(UPLOAD_DIR.glob('*.zip')):
        files.append({
            "id": file_path.name,
            "file_url": f"{base_url}/{file_path.name}",
            "size": file_path.stat().st_size
        })
    
    return jsonify(files)

@app.route('/files/<path:filename>')
def serve_file(filename):
    file_path = UPLOAD_DIR / filename
    if file_path.exists() and file_path.is_file():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
