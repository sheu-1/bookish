from app.extensions import db
from app.models import User, Category, Book, BookVariant

def seed_data():
    db.create_all()

    # 1. Create Default Users if not exist
    admin = User.query.filter_by(email="admin@bookish.co").first()
    if not admin:
        admin = User(name="Bookish Admin", email="admin@bookish.co", phone="+254711000111", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)

    demo_user = User.query.filter_by(email="jane@example.com").first()
    if not demo_user:
        demo_user = User(name="Jane Mwangi", email="jane@example.com", phone="+254722000222", is_admin=False)
        demo_user.set_password("secret123")
        db.session.add(demo_user)

    db.session.commit()

    # 2. Categories with explicit, clear naming
    categories_data = [
        {"name": "Fiction", "slug": "fiction", "colour_token": "violet"},
        {"name": "Finance & Business", "slug": "business", "colour_token": "sunshine"},
        {"name": "Programming & Tech", "slug": "programming", "colour_token": "mint"},
        {"name": "Kids & Young Readers", "slug": "kids", "colour_token": "pink"},
        {"name": "Self-growth", "slug": "self-growth", "colour_token": "mint"},
        {"name": "Romance", "slug": "romance", "colour_token": "pink"},
    ]

    cat_map = {}
    for c in categories_data:
        cat = Category.query.filter_by(slug=c["slug"]).first()
        if not cat:
            cat = Category(name=c["name"], slug=c["slug"], colour_token=c["colour_token"])
            db.session.add(cat)
            db.session.flush()
        else:
            cat.name = c["name"]
            cat.colour_token = c["colour_token"]
        cat_map[c["slug"]] = cat

    db.session.commit()

    # 3. Sample Books with rich summaries, accurate categorization, and CDN covers
    sample_books = [
        {
            "title": "Tomorrow, and Tomorrow, and Tomorrow",
            "slug": "tomorrow-and-tomorrow-and-tomorrow",
            "author": "Gabrielle Zevin",
            "description": "On a bitter-cold day in December, Sam Masur exits a crowded subway car and sees Sadie Green. For a moment, she pretends not to notice him, but then a game begins: a legendary creative partnership that will launch them into video game superstardom. Spanning thirty years, this acclaimed novel explores the intimacies of friendship, artistic passion, grief, and the redemptive power of play.",
            "category": "fiction",
            "price_kes": 1850,
            "stock": 25,
            "tag": "Bestseller",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780593321201-L.jpg",
            "cover_bg": "#6C3BFF",
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",
            "cover_shape": "circle",
        },
        {
            "title": "Atomic Habits",
            "slug": "atomic-habits",
            "author": "James Clear",
            "description": "No matter your goals, Atomic Habits offers a proven, science-backed framework for improving every day. James Clear reveals how tiny, 1% daily adjustments compound into massive long-term success. Discover how to make good habits inevitable and bad habits impossible through the Four Laws of Behavior Change.",
            "category": "self-growth",
            "price_kes": 1950,
            "stock": 30,
            "tag": "Staff pick",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg",
            "cover_bg": "#2EC4A0",
            "cover_fg": "#1B1340",
            "cover_accent": "#1B1340",
            "cover_shape": "arch",
        },
        {
            "title": "The Psychology of Money",
            "slug": "the-psychology-of-money",
            "author": "Morgan Housel",
            "description": "Doing well with money is not simply about mathematics or financial equations—it is about how you behave. In The Psychology of Money, Morgan Housel shares 19 short, captivating stories exploring the strange ways humans perceive wealth, risk, ego, and happiness. A modern finance classic for every investor.",
            "category": "business",
            "price_kes": 1650,
            "stock": 20,
            "tag": "Bestseller",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780857197689-L.jpg",
            "cover_bg": "#FFD23F",
            "cover_fg": "#1B1340",
            "cover_accent": "#FF6B35",
            "cover_shape": "rounded_square",
        },
        {
            "title": "The Boy, The Mole, The Fox and The Horse",
            "slug": "the-boy-the-mole-the-fox-and-the-horse",
            "author": "Charlie Mackesy",
            "description": "A universal tale of hope, friendship, vulnerability, and gentle wisdom for all ages. Enter the world of four unlikely companions navigating the wild together and asking life's greatest questions. Accompanied by Charlie Mackesy's renowned ink and watercolor illustrations, this book has touched millions of hearts worldwide.",
            "category": "kids",
            "price_kes": 2100,
            "stock": 18,
            "tag": "Kids favourite",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780062976581-L.jpg",
            "cover_bg": "#FF8FB1",
            "cover_fg": "#1B1340",
            "cover_accent": "#6C3BFF",
            "cover_shape": "leaf",
        },
        {
            "title": "Yellowface",
            "slug": "yellowface",
            "author": "R.F. Kuang",
            "description": "What is the harm in taking someone else's story, if you are the one who can tell it? When celebrated author Athena Liu dies in a freak accident, struggling writer June Hayward steals Athena's finished draft and claims it as her own. A darkly satirical thriller about cultural appropriation, white privilege, literary jealousy, and the relentless pressure of social media stardom.",
            "category": "fiction",
            "price_kes": 1750,
            "stock": 22,
            "tag": "New",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780063250833-L.jpg",
            "cover_bg": "#FFD23F",
            "cover_fg": "#1B1340",
            "cover_accent": "#1B1340",
            "cover_shape": "arch",
        },
        {
            "title": "Build: An Unorthodox Guide to Making Things Worth Making",
            "slug": "build-tony-fadell",
            "author": "Tony Fadell",
            "description": "Tony Fadell led the teams that created the iPod, the iPhone, and the Nest Learning Thermostat. Build delivers pragmatic mentorship forged across thirty-plus years in Silicon Valley—from handling workplace conflict and choosing startup co-founders to product design principles that thrill customers.",
            "category": "business",
            "price_kes": 2250,
            "stock": 14,
            "tag": "Staff pick",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9781787634114-L.jpg",
            "cover_bg": "#FF6B35",
            "cover_fg": "#1B1340",
            "cover_accent": "#FFFFFF",
            "cover_shape": "rounded_square",
        },
        {
            "title": "The Seven Husbands of Evelyn Hugo",
            "slug": "the-seven-husbands-of-evelyn-hugo",
            "author": "Taylor Jenkins Reid",
            "description": "Aging Hollywood movie siren Evelyn Hugo is finally ready to reveal the unfiltered truth about her glamorous, scandalous, and secretive life. She summons unknown journalist Monique Grant to dictate her tell-all biography. A spellbinding story of ambition, resilience, and an enduring forbidden romance.",
            "category": "romance",
            "price_kes": 1600,
            "stock": 28,
            "tag": "Bestseller",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9781501161933-L.jpg",
            "cover_bg": "#0E6B56",
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",
            "cover_shape": "leaf",
        },
        {
            "title": "Big Magic: Creative Living Beyond Fear",
            "slug": "big-magic",
            "author": "Elizabeth Gilbert",
            "description": "Elizabeth Gilbert invites readers to embark on creative journeys free from shame, fear, and perfectionism. In Big Magic, she demystifies the creative process with warmth and generous humor. Whether you desire to write a book, paint, dance, or start a passion project, this inspiring book unlocks human imagination and courage.",
            "category": "self-growth",
            "price_kes": 1500,
            "stock": 19,
            "tag": "New",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9781594634727-L.jpg",
            "cover_bg": "#2F6BFF",
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FF8FB1",
            "cover_shape": "circle",
        },
        {
            "title": "Where the Wild Things Are",
            "slug": "where-the-wild-things-are",
            "author": "Maurice Sendak",
            "description": "When young Max puts on his wolf suit and misbehaves, his mother sends him to bed without supper. Soon, a magical forest sprouts in his bedroom, leading him to a private sailboat that journeys to where the Wild Things roar and dance. A beloved Caldecott-winning children's masterpiece celebrating imagination and resilience.",
            "category": "kids",
            "price_kes": 1350,
            "stock": 16,
            "tag": "Kids favourite",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780060254926-L.jpg",
            "cover_bg": "#2EC4A0",
            "cover_fg": "#1B1340",
            "cover_accent": "#FFD23F",
            "cover_shape": "arch",
        },
        {
            "title": "Book Lovers",
            "slug": "book-lovers",
            "author": "Emily Henry",
            "description": "Nora Stephens is an ambitious New York literary agent who is always the 'villain' in classic rom-coms. Charlie Lastra is a brooding, hypercritical book editor who knows all of Nora's secrets. When both end up in the quaint North Carolina village of Sunshine Falls for the summer, their fiery rivalries ignite into a witty, heartfelt love story.",
            "category": "romance",
            "price_kes": 1700,
            "stock": 25,
            "tag": "New",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780593334836-L.jpg",
            "cover_bg": "#FF8FB1",
            "cover_fg": "#1B1340",
            "cover_accent": "#FFD23F",
            "cover_shape": "circle",
        },
        {
            "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
            "slug": "clean-code",
            "author": "Robert C. Martin",
            "description": "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. Master software expert Robert C. Martin presents a revolutionary paradigm with Clean Code. Packed with real-world case studies and pragmatic refactoring techniques every engineer must know.",
            "category": "programming",
            "price_kes": 999,
            "stock": 25,
            "tag": "Bestseller",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780132350884-L.jpg",
            "cover_bg": "#2F6BFF",
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",
            "cover_shape": "arch",
        },
        {
            "title": "The Pragmatic Programmer",
            "slug": "the-pragmatic-programmer",
            "author": "David Thomas, Andrew Hunt",
            "description": "Your journey to mastery. The Pragmatic Programmer illustrates the core principles of software craftsmanship, helping engineers avoid the pitfalls of software development. Topics range from personal responsibility and career development to architectural techniques for keeping your code flexible.",
            "category": "programming",
            "price_kes": 999,
            "stock": 30,
            "tag": "Staff pick",
            "cover_image": "https://covers.openlibrary.org/b/isbn/9780135957059-L.jpg",
            "cover_bg": "#6C3BFF",
            "cover_fg": "#FFFFFF",
            "cover_accent": "#2EC4A0",
            "cover_shape": "circle",
        },
    ]

    for b_data in sample_books:
        book = Book.query.filter_by(slug=b_data["slug"]).first()
        cat = cat_map[b_data["category"]]
        if not book:
            book = Book(
                title=b_data["title"],
                slug=b_data["slug"],
                author=b_data["author"],
                description=b_data["description"],
                category_id=cat.id,
                price_kes=b_data["price_kes"],
                stock=b_data["stock"],
                tag=b_data.get("tag"),
                cover_image=b_data.get("cover_image"),
                cover_bg=b_data["cover_bg"],
                cover_fg=b_data["cover_fg"],
                cover_accent=b_data["cover_accent"],
                cover_shape=b_data["cover_shape"],
                is_active=True,
            )
            db.session.add(book)
            db.session.flush()
        else:
            book.category_id = cat.id
            book.description = b_data["description"]
            book.price_kes = b_data["price_kes"]
            book.tag = b_data.get("tag")
            book.is_active = True
            if b_data.get("cover_image"):
                book.cover_image = b_data["cover_image"]

    db.session.commit()

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_data()
        print("Database seeded with books, categories and updated prices!")
