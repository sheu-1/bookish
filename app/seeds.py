from app.extensions import db
from app.models import User, Category, Book, BookVariant

categories_data = [
    {"name": "African Literature & Voices", "slug": "african-lit", "colour_token": "mint"},
    {"name": "Biographies & Memoirs", "slug": "biography", "colour_token": "tangerine"},
    {"name": "Finance & Business", "slug": "business", "colour_token": "sunshine"},
    {"name": "Fiction", "slug": "fiction", "colour_token": "violet"},
    {"name": "Sci-Fi & Fantasy", "slug": "scifi-fantasy", "colour_token": "violet"},
    {"name": "Self-growth", "slug": "self-growth", "colour_token": "mint"},
    {"name": "Romance", "slug": "romance", "colour_token": "pink"},
    {"name": "Kids & Young Readers", "slug": "kids", "colour_token": "pink"},
    {"name": "Programming & Tech", "slug": "programming", "colour_token": "mint"},
]

sample_books = [
    # --- AFRICAN LITERATURE & VOICES ---
    {
        "title": "Born a Crime: Stories from a South African Childhood",
        "slug": "born-a-crime",
        "author": "Trevor Noah",
        "description": "Trevor Noah's unlikely path from apartheid South Africa to the desk of The Daily Show began with a criminal act: his birth. Trevor was born to a white Swiss father and a Black Xhosa mother, at a time when such a union was punishable by five years in prison. Living proof of his parents' indiscretion, Trevor was kept mostly indoors for the earliest years of his life. A compelling, inspiring, and comically candid memoir.",
        "category": "african-lit",
        "price_kes": 1750,
        "stock": 25,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780399588198-L.jpg",
        "cover_bg": "#FF6B35",
        "cover_fg": "#1B1340",
        "cover_accent": "#FFD23F",
        "cover_shape": "arch",
    },
    {
        "title": "Americanah",
        "slug": "americanah",
        "author": "Chimamanda Ngozi Adichie",
        "description": "As teenagers in a Lagos secondary school, Ifemelu and Obinze fell in love. Their Nigeria was under military dictatorship, and people were fleeing if they could. Beautiful, self-assured Ifemelu departed for America, where she suffered defeats and triumphs, while quiet Obinze plunged into a dangerous, undocumented life in London. A fearless story about love, race, and identity across three continents.",
        "category": "african-lit",
        "price_kes": 1650,
        "stock": 20,
        "tag": "Staff pick",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780307455925-L.jpg",
        "cover_bg": "#2EC4A0",
        "cover_fg": "#1B1340",
        "cover_accent": "#FF8FB1",
        "cover_shape": "leaf",
    },
    {
        "title": "Things Fall Apart",
        "slug": "things-fall-apart",
        "author": "Chinua Achebe",
        "description": "The quintessential African novel that introduced modern African literature to the global stage. Okonkwo is a wealthy and respected warrior of the Umuofia clan, determined never to be like his idle father. When British colonialists and Christian missionaries arrive, the fabric of traditional Igbo society unravels in a powerful, tragic collision of worlds.",
        "category": "african-lit",
        "price_kes": 1250,
        "stock": 35,
        "tag": "Classic",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780385474542-L.jpg",
        "cover_bg": "#FFD23F",
        "cover_fg": "#1B1340",
        "cover_accent": "#0E6B56",
        "cover_shape": "circle",
    },

    # --- BIOGRAPHIES & MEMOIRS ---
    {
        "title": "Shoe Dog: A Memoir by the Creator of Nike",
        "slug": "shoe-dog",
        "author": "Phil Knight",
        "description": "In 1962, fresh out of business school, Phil Knight borrowed fifty dollars from his father and launched a company with one simple mission: import high-quality, low-cost running shoes from Japan. Selling the shoes from the trunk of his car, Knight grossed eight thousand dollars in his first year. Today, Nike's annual sales top thirty billion. An intimate, illuminating, and gritty journey of building an icon from scratch.",
        "category": "biography",
        "price_kes": 1950,
        "stock": 22,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9781501135927-L.jpg",
        "cover_bg": "#FF6B35",
        "cover_fg": "#1B1340",
        "cover_accent": "#FFFFFF",
        "cover_shape": "rounded_square",
    },
    {
        "title": "Becoming",
        "slug": "becoming",
        "author": "Michelle Obama",
        "description": "An intimate, powerful, and inspiring memoir by the former First Lady of the United States. In a life filled with meaning and accomplishment, Michelle Obama emerged as one of the most iconic women of our era. With unerring honesty and lively wit, she describes her triumphs and disappointments, recounting how she found her voice.",
        "category": "biography",
        "price_kes": 2100,
        "stock": 18,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9781524763138-L.jpg",
        "cover_bg": "#6C3BFF",
        "cover_fg": "#FFFFFF",
        "cover_accent": "#FFD23F",
        "cover_shape": "circle",
    },
    {
        "title": "Educated: A Memoir",
        "slug": "educated",
        "author": "Tara Westover",
        "description": "Born to survivalists in the mountains of Idaho, Tara Westover was seventeen the first time she set foot in a classroom. Her family was so isolated from mainstream society that there was no one to ensure the children received an education. When another brother got into college, Tara decided to try a new kind of life. An extraordinary story of resilience, self-invention, and the power of knowledge.",
        "category": "biography",
        "price_kes": 1800,
        "stock": 20,
        "tag": "Staff pick",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780399590504-L.jpg",
        "cover_bg": "#FFD23F",
        "cover_fg": "#1B1340",
        "cover_accent": "#2EC4A0",
        "cover_shape": "arch",
    },

    # --- SCI-FI & FANTASY ---
    {
        "title": "Dune",
        "slug": "dune",
        "author": "Frank Herbert",
        "description": "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world where the only thing of value is the 'spice' melange. A triumph of the imagination and one of the bestselling science fiction novels of all time.",
        "category": "scifi-fantasy",
        "price_kes": 1850,
        "stock": 25,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780441172719-L.jpg",
        "cover_bg": "#FFD23F",
        "cover_fg": "#1B1340",
        "cover_accent": "#FF6B35",
        "cover_shape": "arch",
    },
    {
        "title": "Project Hail Mary",
        "slug": "project-hail-mary",
        "author": "Andy Weir",
        "description": "Ryland Grace is the sole survivor on a desperate, last-chance mission—and if he fails, humanity and the earth itself are doomed. Except right now, he doesn't know that. He can't even remember his own name. A lone astronaut must solve an extinction-level mystery with science, ingenuity, and an unexpected extraterrestrial ally.",
        "category": "scifi-fantasy",
        "price_kes": 1950,
        "stock": 16,
        "tag": "Staff pick",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780593135204-L.jpg",
        "cover_bg": "#1B1340",
        "cover_fg": "#FFFFFF",
        "cover_accent": "#FFD23F",
        "cover_shape": "circle",
    },

    # --- FINANCE & BUSINESS ---
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
        "title": "Rich Dad Poor Dad",
        "slug": "rich-dad-poor-dad",
        "author": "Robert T. Kiyosaki",
        "description": "What the rich teach their kids about money that the poor and middle class do not! Explodes the myth that you need to earn a high income to be rich and explains the difference between working for money and having your money work for you through assets and investing.",
        "category": "business",
        "price_kes": 1450,
        "stock": 30,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9781612680194-L.jpg",
        "cover_bg": "#6C3BFF",
        "cover_fg": "#FFFFFF",
        "cover_accent": "#FFD23F",
        "cover_shape": "circle",
    },
    {
        "title": "The Intelligent Investor",
        "slug": "the-intelligent-investor",
        "author": "Benjamin Graham",
        "description": "The definitive book on value investing. Benjamin Graham's philosophy of 'value investing' shields investors from substantial error and teaches them to develop long-term strategies that have made this book an investment bible since its original publication in 1949.",
        "category": "business",
        "price_kes": 2100,
        "stock": 15,
        "tag": "Classic",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780060555665-L.jpg",
        "cover_bg": "#0E6B56",
        "cover_fg": "#FFFFFF",
        "cover_accent": "#FFD23F",
        "cover_shape": "leaf",
    },

    # --- SELF-GROWTH ---
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
        "title": "Deep Work: Rules for Focused Success in a Distracted World",
        "slug": "deep-work",
        "author": "Cal Newport",
        "description": "Deep work is the ability to focus without distraction on a cognitively demanding task. It's a skill that allows you to quickly master complicated information and produce better results in less time. Cal Newport makes the case that in an increasingly noisy world, the ability to concentrate deeply is the superpower of the knowledge economy.",
        "category": "self-growth",
        "price_kes": 1750,
        "stock": 25,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9781455586691-L.jpg",
        "cover_bg": "#FFD23F",
        "cover_fg": "#1B1340",
        "cover_accent": "#FF6B35",
        "cover_shape": "rounded_square",
    },
    {
        "title": "Thinking, Fast and Slow",
        "slug": "thinking-fast-and-slow",
        "author": "Daniel Kahneman",
        "description": "Nobel laureate Daniel Kahneman takes us on a groundbreaking tour of the mind, explaining the two systems that drive the way we think: System 1 is fast, intuitive, and emotional; System 2 is slower, more deliberative, and more logical. Engaging minds and reshaping our understanding of intuition, choices, and behavioral economics.",
        "category": "self-growth",
        "price_kes": 1900,
        "stock": 20,
        "tag": "Staff pick",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg",
        "cover_bg": "#2EC4A0",
        "cover_fg": "#1B1340",
        "cover_accent": "#6C3BFF",
        "cover_shape": "circle",
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

    # --- FICTION ---
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

    # --- ROMANCE ---
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

    # --- KIDS & YOUNG READERS ---
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

    # --- PROGRAMMING & TECH ---
    {
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "slug": "clean-code",
        "author": "Robert C. Martin",
        "description": "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. Master software expert Robert C. Martin presents a revolutionary paradigm with Clean Code. Packed with real-world case studies and pragmatic refactoring techniques every engineer must know.",
        "category": "programming",
        "price_kes": 1950,
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
        "price_kes": 2100,
        "stock": 30,
        "tag": "Staff pick",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9780135957059-L.jpg",
        "cover_bg": "#6C3BFF",
        "cover_fg": "#FFFFFF",
        "cover_accent": "#2EC4A0",
        "cover_shape": "circle",
    },
    {
        "title": "Designing Data-Intensive Applications",
        "slug": "designing-data-intensive-applications",
        "author": "Martin Kleppmann",
        "description": "The big ideas behind reliable, scalable, and maintainable systems. Martin Kleppmann helps you navigate the diverse and fast-changing landscape of technologies for storing and processing data. Peer under the hood of databases, distributed systems, replication, partitioning, and stream processing.",
        "category": "programming",
        "price_kes": 2400,
        "stock": 20,
        "tag": "Bestseller",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9781449373320-L.jpg",
        "cover_bg": "#0E6B56",
        "cover_fg": "#FFFFFF",
        "cover_accent": "#FF6B35",
        "cover_shape": "leaf",
    },
    {
        "title": "Automate the Boring Stuff with Python",
        "slug": "automate-the-boring-stuff",
        "author": "Al Sweigart",
        "description": "Practical programming for total beginners. If you've ever spent hours renaming files or updating hundreds of spreadsheet cells, you know how tedious tasks can be. Learn how to write simple Python programs to do in minutes what would take you hours by hand.",
        "category": "programming",
        "price_kes": 1800,
        "stock": 25,
        "tag": "New",
        "cover_image": "https://covers.openlibrary.org/b/isbn/9781593279929-L.jpg",
        "cover_bg": "#FFD23F",
        "cover_fg": "#1B1340",
        "cover_accent": "#2F6BFF",
        "cover_shape": "rounded_square",
    },
]

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

    # 2. Categories
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

    # 3. Seed books
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
            book.title = b_data["title"]
            book.author = b_data["author"]
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
