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

    # 3. Sample Books matching the design canvas and spec with rich summaries
    sample_books = [
        # --- FINANCIAL BOOKS (Priced at 200 KES) ---
        {
            "title": "The Psychology of Money",
            "slug": "the-psychology-of-money",
            "author": "Morgan Housel",
            "description": "Doing well with money is not simply about mathematics or financial equations—it is about how you behave. In The Psychology of Money, Morgan Housel shares 19 short, captivating stories exploring the strange ways humans perceive wealth, risk, ego, and happiness.\n\nYou will learn why financial freedom is really about sleeping well at night, how compounding works in the real world, and why keeping money requires humility while making money requires risk. A modern finance classic for every investor.",
            "category": "business",
            "price_kes": 200,
            "stock": 25,
            "tag": "Bestseller",
            "cover_image": "/static/img/covers/the-psychology-of-money.jpg",
            "cover_bg": "#FFD23F",       # sunshine
            "cover_fg": "#1B1340",
            "cover_accent": "#FF6B35",   # tangerine
            "cover_shape": "rounded_square",
            "variants": [
                ("Paperback", 200, 25),
                ("Hardcover", 200, 10),
                ("eBook", 200, 100),
            ]
        },
        {
            "title": "Rich Dad Poor Dad",
            "slug": "rich-dad-poor-dad",
            "author": "Robert T. Kiyosaki",
            "description": "What the rich teach their kids about money that the poor and middle class do not! Explodes the myth that you need to earn a high income to be rich and explains the difference between working for money and having your money work for you.",
            "category": "business",
            "price_kes": 200,
            "stock": 30,
            "tag": "Bestseller",
            "cover_image": None,
            "cover_bg": "#2EC4A0",       # mint
            "cover_fg": "#1B1340",
            "cover_accent": "#FFD23F",   # sunshine
            "cover_shape": "circle",
            "variants": [
                ("Paperback", 200, 20),
                ("Hardcover", 200, 10),
                ("eBook", 200, 100),
            ]
        },
        {
            "title": "The Intelligent Investor",
            "slug": "the-intelligent-investor",
            "author": "Benjamin Graham",
            "description": "The definitive book on value investing. Benjamin Graham's philosophy of 'value investing' shields investors from substantial error and teaches them to develop long-term strategies that have made this book an investment bible.",
            "category": "business",
            "price_kes": 200,
            "stock": 20,
            "tag": "Staff pick",
            "cover_image": None,
            "cover_bg": "#0E6B56",       # forest
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",   # sunshine
            "cover_shape": "leaf",
            "variants": [
                ("Paperback", 200, 15),
                ("Hardcover", 200, 5),
            ]
        },
        {
            "title": "Build: An Unorthodox Guide to Making Things Worth Making",
            "slug": "build-tony-fadell",
            "author": "Tony Fadell",
            "description": "Tony Fadell led the teams that created the iPod, the iPhone, and the Nest Learning Thermostat. Build delivers pragmatic mentorship forged across thirty-plus years in Silicon Valley.\n\nFrom handling workplace conflict and choosing startup co-founders to product design principles that thrill customers, this is the definitive playbook for makers, managers, and entrepreneurs.",
            "category": "business",
            "price_kes": 200,
            "stock": 14,
            "tag": "Staff pick",
            "cover_image": "/static/img/covers/build-tony-fadell.jpg",
            "cover_bg": "#FF6B35",       # tangerine
            "cover_fg": "#1B1340",
            "cover_accent": "#FFFFFF",
            "cover_shape": "rounded_square",
            "variants": [
                ("Hardcover", 200, 10),
                ("Paperback", 200, 15),
            ]
        },

        # --- PROGRAMMING BOOKS (Priced at 999 KES) ---
        {
            "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
            "slug": "clean-code",
            "author": "Robert C. Martin",
            "description": "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. Master software expert Robert C. Martin presents a revolutionary paradigm with Clean Code.\n\nLearn how to write code that is clean, readable, robust, and maintainable. Packed with real-world case studies and pragmatic refactoring techniques every software engineer must know.",
            "category": "programming",
            "price_kes": 999,
            "stock": 25,
            "tag": "Bestseller",
            "cover_image": None,
            "cover_bg": "#2F6BFF",       # blue
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",   # sunshine
            "cover_shape": "arch",
            "variants": [
                ("Paperback", 999, 20),
                ("Hardcover", 999, 5),
                ("eBook", 999, 100),
            ]
        },
        {
            "title": "The Pragmatic Programmer",
            "slug": "the-pragmatic-programmer",
            "author": "David Thomas, Andrew Hunt",
            "description": "Your journey to mastery. The Pragmatic Programmer illustrates the core principles of software craftsmanship, helping engineers avoid the pitfalls of software development.\n\nTopics range from personal responsibility and career development to architectural techniques for keeping your code flexible and easy to adapt and reuse.",
            "category": "programming",
            "price_kes": 999,
            "stock": 30,
            "tag": "Staff pick",
            "cover_image": None,
            "cover_bg": "#6C3BFF",       # violet
            "cover_fg": "#FFFFFF",
            "cover_accent": "#2EC4A0",   # mint
            "cover_shape": "circle",
            "variants": [
                ("Paperback", 999, 25),
                ("Hardcover", 999, 5),
            ]
        },
        {
            "title": "Automate the Boring Stuff with Python",
            "slug": "automate-the-boring-stuff",
            "author": "Al Sweigart",
            "description": "Practical programming for total beginners. If you've ever spent hours renaming files or updating hundreds of spreadsheet cells, you know how tedious tasks can be. Learn how to write simple Python programs to do in minutes what would take you hours by hand.",
            "category": "programming",
            "price_kes": 999,
            "stock": 28,
            "tag": "New",
            "cover_image": None,
            "cover_bg": "#FFD23F",       # sunshine
            "cover_fg": "#1B1340",
            "cover_accent": "#2F6BFF",   # blue
            "cover_shape": "rounded_square",
            "variants": [
                ("Paperback", 999, 20),
                ("eBook", 999, 100),
            ]
        },
        {
            "title": "Designing Data-Intensive Applications",
            "slug": "designing-data-intensive-applications",
            "author": "Martin Kleppmann",
            "description": "The big ideas behind reliable, scalable, and maintainable systems. Martin Kleppmann helps you navigate the diverse and fast-changing landscape of technologies for processing and storing data.\n\nPeer under the hood of databases, distributed systems, replication, partitioning, transactions, and stream processing.",
            "category": "programming",
            "price_kes": 999,
            "stock": 18,
            "tag": "Bestseller",
            "cover_image": None,
            "cover_bg": "#0E6B56",       # forest
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FF6B35",   # tangerine
            "cover_shape": "leaf",
            "variants": [
                ("Paperback", 999, 12),
                ("Hardcover", 999, 6),
            ]
        },
        {
            "title": "Python Crash Course",
            "slug": "python-crash-course",
            "author": "Eric Matthes",
            "description": "A hands-on, project-based introduction to programming. Python Crash Course is the world's best-selling guide to the Python programming language.\n\nThis fast-paced, thorough introduction will have you writing programs, solving problems, and developing functional web applications in no time.",
            "category": "programming",
            "price_kes": 999,
            "stock": 24,
            "tag": "Staff pick",
            "cover_image": None,
            "cover_bg": "#2EC4A0",       # mint
            "cover_fg": "#1B1340",
            "cover_accent": "#6C3BFF",   # violet
            "cover_shape": "circle",
            "variants": [
                ("Paperback", 999, 20),
                ("eBook", 999, 100),
            ]
        },

        # --- OTHER FICTION & GENERAL BOOKS ---
        {
            "title": "Tomorrow, and Tomorrow, and Tomorrow",
            "slug": "tomorrow-and-tomorrow-and-tomorrow",
            "author": "Gabrielle Zevin",
            "description": "On a bitter-cold day in December, Sam Masur exits a crowded subway car and sees Sadie Green. For a moment, she pretends not to notice him, but then a game begins: a legendary creative partnership that will launch them into video game superstardom.\n\nSpanning thirty years, from Cambridge to Venice Beach, this acclaimed novel explores the intimacies of friendship, artistic passion, grief, and the redemptive power of play. It is an unforgettable ode to connection and identity.",
            "category": "fiction",
            "price_kes": 1850,
            "stock": 25,
            "tag": "Bestseller",
            "cover_image": "/static/img/covers/tomorrow-and-tomorrow-and-tomorrow.jpg",
            "cover_bg": "#6C3BFF",       # violet
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",   # sunshine
            "cover_shape": "circle",
            "variants": [
                ("Paperback", 1850, 15),
                ("Hardcover", 2600, 8),
                ("eBook", 950, 100),
            ]
        },
        {
            "title": "Atomic Habits",
            "slug": "atomic-habits",
            "author": "James Clear",
            "description": "No matter your goals, Atomic Habits offers a proven, science-backed framework for improving every day. James Clear reveals how tiny, 1% daily adjustments compound into massive long-term success.\n\nDiscover how to make good habits inevitable and bad habits impossible through the Four Laws of Behavior Change. If you have struggled to sustain routines, the problem is not your willpower—it is your system. An essential manual for mastery and personal growth.",
            "category": "self-growth",
            "price_kes": 1950,
            "stock": 30,
            "tag": "Staff pick",
            "cover_image": "/static/img/covers/atomic-habits.jpg",
            "cover_bg": "#2EC4A0",       # mint
            "cover_fg": "#1B1340",       # ink
            "cover_accent": "#1B1340",
            "cover_shape": "arch",
            "variants": [
                ("Paperback", 1950, 20),
                ("Hardcover", 2800, 10),
                ("eBook", 1100, 100),
            ]
        },
        {
            "title": "The Boy, The Mole, The Fox and The Horse",
            "slug": "the-boy-the-mole-the-fox-and-the-horse",
            "author": "Charlie Mackesy",
            "description": "A universal tale of hope, friendship, vulnerability, and gentle wisdom for all ages. Enter the world of four unlikely companions navigating the wild together and asking life's greatest questions.\n\nAccompanied by Charlie Mackesy's renowned ink and watercolor illustrations, this book has touched millions of hearts worldwide with its comforting reminder that asking for help is the bravest thing you can do.",
            "category": "kids",
            "price_kes": 2100,
            "stock": 18,
            "tag": "Kids favourite",
            "cover_image": "/static/img/covers/the-boy-the-mole-the-fox-and-the-horse.jpg",
            "cover_bg": "#FF8FB1",       # pink
            "cover_fg": "#1B1340",
            "cover_accent": "#6C3BFF",   # violet
            "cover_shape": "leaf",
            "variants": [
                ("Hardcover", 2100, 18),
                ("Paperback", 1550, 12),
            ]
        },
        {
            "title": "Yellowface",
            "slug": "yellowface",
            "author": "R.F. Kuang",
            "description": "What is the harm in taking someone else's story, if you are the one who can tell it? When celebrated author Athena Liu dies in a freak pancake accident, struggling writer June Hayward steals Athena's finished draft about Chinese laborers in WWI and claims it as her own.\n\nA wildly entertaining, darkly satirical thriller about cultural appropriation, white privilege, literary jealousy, and the relentless pressure of social media stardom.",
            "category": "fiction",
            "price_kes": 1750,
            "stock": 22,
            "tag": "New",
            "cover_image": "/static/img/covers/yellowface.jpg",
            "cover_bg": "#FFD23F",       # sunshine
            "cover_fg": "#1B1340",
            "cover_accent": "#1B1340",
            "cover_shape": "arch",
            "variants": [
                ("Paperback", 1750, 16),
                ("Hardcover", 2500, 6),
                ("eBook", 900, 100),
            ]
        },
        {
            "title": "The Seven Husbands of Evelyn Hugo",
            "slug": "the-seven-husbands-of-evelyn-hugo",
            "author": "Taylor Jenkins Reid",
            "description": "Aging Hollywood movie siren Evelyn Hugo is finally ready to reveal the unfiltered truth about her glamorous, scandalous, and secretive life. She summons unknown journalist Monique Grant to dictate her tell-all biography.\n\nFrom 1950s cinema sets to private tragedies and unforgettable secrets, Evelyn weaves a spellbinding story of ambition, resilience, and an enduring forbidden romance.",
            "category": "romance",
            "price_kes": 1600,
            "stock": 28,
            "tag": "Bestseller",
            "cover_image": "/static/img/covers/the-seven-husbands-of-evelyn-hugo.jpg",
            "cover_bg": "#0E6B56",       # forest
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FFD23F",   # sunshine
            "cover_shape": "leaf",
            "variants": [
                ("Paperback", 1600, 20),
                ("Hardcover", 2300, 8),
                ("eBook", 800, 100),
            ]
        },
        {
            "title": "Big Magic: Creative Living Beyond Fear",
            "slug": "big-magic",
            "author": "Elizabeth Gilbert",
            "description": "Elizabeth Gilbert invites readers to embark on creative journeys free from shame, fear, and perfectionism. In Big Magic, she demystifies the creative process with warmth and generous humor.\n\nWhether you desire to write a book, paint, dance, or start a passion project, this inspiring book unlocks the mystical relationship between human imagination and courage.",
            "category": "self-growth",
            "price_kes": 1500,
            "stock": 19,
            "tag": "New",
            "cover_image": "/static/img/covers/big-magic.jpg",
            "cover_bg": "#2F6BFF",       # blue
            "cover_fg": "#FFFFFF",
            "cover_accent": "#FF8FB1",   # pink
            "cover_shape": "circle",
            "variants": [
                ("Paperback", 1500, 15),
                ("Hardcover", 2200, 4),
            ]
        },
        {
            "title": "Where the Wild Things Are",
            "slug": "where-the-wild-things-are",
            "author": "Maurice Sendak",
            "description": "When young Max puts on his wolf suit and misbehaves, his mother sends him to bed without supper. Soon, a magical forest sprouts in his bedroom, leading him to a private sailboat that journeys to where the Wild Things roar and dance.\n\nA beloved, Caldecott-winning children's masterpiece that celebrates boundless imagination, emotional resilience, and the comfort of returning home.",
            "category": "kids",
            "price_kes": 1350,
            "stock": 16,
            "tag": "Kids favourite",
            "cover_image": "/static/img/covers/where-the-wild-things-are.jpg",
            "cover_bg": "#2EC4A0",       # mint
            "cover_fg": "#1B1340",
            "cover_accent": "#FFD23F",
            "cover_shape": "arch",
            "variants": [
                ("Paperback", 1350, 12),
                ("Hardcover", 1950, 4),
            ]
        },
        {
            "title": "Book Lovers",
            "slug": "book-lovers",
            "author": "Emily Henry",
            "description": "Nora Stephens is an ambitious New York literary agent who is always the 'villain' in classic rom-coms. Charlie Lastra is a brooding, hypercritical book editor who knows all of Nora's secrets.\n\nWhen both end up in the quaint North Carolina village of Sunshine Falls for the summer, their fiery rivalries ignite into a witty, heartfelt love story that defies romantic cliches.",
            "category": "romance",
            "price_kes": 1700,
            "stock": 25,
            "tag": "New",
            "cover_image": "/static/img/covers/book-lovers.jpg",
            "cover_bg": "#FF8FB1",       # pink
            "cover_fg": "#1B1340",
            "cover_accent": "#FFD23F",
            "cover_shape": "circle",
            "variants": [
                ("Paperback", 1700, 18),
                ("Hardcover", 2450, 7),
                ("eBook", 850, 100),
            ]
        }
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
            # Update category, description, pricing, and active status
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
