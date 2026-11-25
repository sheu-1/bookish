import requests
from pathlib import Path
from app import create_app
from app.extensions import db
from app.models import Book

COVERS_DIR = Path(__file__).resolve().parent / "static" / "img" / "covers"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

# Verified ISBN-13 lists per book slug (primary + alternate editions)
BOOK_ISBNS_MAP = {
    "the-psychology-of-money": ["9780857197689", "9780857199096"],
    "atomic-habits": ["9780735211292", "9781847941831"],
    "tomorrow-and-tomorrow-and-tomorrow": ["9780593321201", "9780735243361", "9780593466490"],
    "yellowface": ["9780063250833", "9780063250857"],
    "the-seven-husbands-of-evelyn-hugo": ["9781501161933", "9781501139239", "9781982147662"],
    "the-boy-the-mole-the-fox-and-the-horse": ["9780062976581", "9781529105100"],
    "where-the-wild-things-are": ["9780060254926", "9780064431781", "9780099408390"],
    "big-magic": ["9781594634710", "9781594634727"],
    "book-lovers": ["9780593440872", "9780593334836"],
    "build-tony-fadell": ["9780552177757", "9781787634114", "9780063046061"],
}

def download_and_assign_covers():
    app = create_app()
    with app.app_context():
        headers = {"User-Agent": "BookishStore/1.0 (contact@bookish.co)"}
        for slug, isbns in BOOK_ISBNS_MAP.items():
            book = Book.query.filter_by(slug=slug).first()
            if not book:
                print(f"Book '{slug}' not found in database.")
                continue

            local_filename = f"{slug}.jpg"
            local_path = COVERS_DIR / local_filename
            saved = False

            for isbn in isbns:
                img_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
                try:
                    print(f"Trying '{book.title}' ISBN {isbn}...")
                    resp = requests.get(img_url, headers=headers, timeout=15)
                    if resp.status_code == 200 and len(resp.content) > 5000:
                        with open(local_path, "wb") as f:
                            f.write(resp.content)
                        book.cover_image = f"/static/img/covers/{local_filename}"
                        print(f"-> Saved {local_filename} ({len(resp.content)} bytes)")
                        saved = True
                        break
                    else:
                        print(f"-> Skipped {isbn} (status={resp.status_code}, size={len(resp.content)})")
                except Exception as e:
                    print(f"-> Error for {isbn}: {e}")

            if not saved:
                print(f"WARNING: Could not download cover for '{book.title}'")

        db.session.commit()
        print("Finished updating book covers!")

if __name__ == "__main__":
    download_and_assign_covers()
