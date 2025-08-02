import json
from pathlib import Path

UPLOAD_DIR = Path(__file__).parent / "uploads"
OUTPUT_FILE = Path(__file__).parent / "trd_public.json"

def scan_dir(root: Path):
    items = []
    for p in sorted(root.iterdir()):
        if p.is_dir():
            items.append({
                "type": "dir",
                "name": p.name,
                "children": scan_dir(p)
            })
        else:
            items.append({
                "type": "file",
                "name": p.name,
                "path": str(p.relative_to(UPLOAD_DIR)),
                "size_bytes": p.stat().st_size
            })
    return items

def main():
    tree = scan_dir(UPLOAD_DIR)
    data = {"files": tree}
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
