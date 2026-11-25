import os
import requests
from pathlib import Path
from app import create_app
from app.extensions import db
from app.models import Book

COVERS_DIR = Path(__file__).resolve().parent / "static" / "img" / "covers"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

# Direct OpenLibrary or reliable cover IDs / URLs
BOOK_COVERS_MAP = {
    "the-psychology-of-money": "https://covers.openlibrary.org/b/id/10522818-L.jpg",
    "atomic-habits": "https://covers.openlibrary.org/b/id/12843460-L.jpg",
    "tomorrow-and-tomorrow-and-tomorrow": "https://covers.openlibrary.org/b/id/12836262-L.jpg",
    "yellowface": "https://covers.openlibrary.org/b/id/13460742-L.jpg",
    "the-seven-husbands-of-evelyn-hugo": "https://covers.openlibrary.org/b/id/12665126-L.jpg",
    "the-boy-the-mole-the-fox-and-the-horse": "https://covers.openlibrary.org/b/id/10186100-L.jpg",
    "where-the-wild-things-are": "https://covers.openlibrary.org/b/id/8316269-L.jpg",
    "big-magic": "https://covers.openlibrary.org/b/id/7942718-L.jpg",
    "book-lovers": "https://covers.openlibrary.org/b/id/12648744-L.jpg",
    "build-tony-fadell": "https://covers.openlibrary.org/b/id/12871318-L.jpg",
}

def download_and_assign_covers():
    app = create_app()
    with app.app_context():
        headers = {"User-Agent": "BookishStore/1.0 (contact@bookish.co)"}
        for slug, img_url in BOOK_COVERS_MAP.items():
            book = Book.query.filter_by(slug=slug).first()
            if not book:
                print(f"Book '{slug}' not found in database.")
                continue

            local_filename = f"{slug}.jpg"
            local_path = COVERS_DIR / local_filename

            try:
                print(f"Downloading cover for '{book.title}' from {img_url}...")
                resp = requests.get(img_url, headers=headers, timeout=15)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                    
                    # Store static path in db
                    book.cover_image = f"/static/img/covers/{local_filename}"
                    print(f"-> Successfully saved to {local_path} ({len(resp.content)} bytes)")
                else:
                    print(f"-> Bad response {resp.status_code} or small file ({len(resp.content)} bytes)")
            except Exception as e:
                print(f"-> Error fetching cover for {slug}: {e}")

        db.session.commit()
        print("All covers updated in database successfully!")

if __name__ == "__main__":
    download_and_assign_covers()
