-- ============================================
-- Bookish Online Store — Supabase SQL Schema
-- Run this in Supabase SQL Editor (or psql)
-- ============================================

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    colour_token VARCHAR(50) NOT NULL DEFAULT 'violet'
);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

-- 3. Books
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    author VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    price_kes INTEGER NOT NULL,
    stock INTEGER NOT NULL DEFAULT 10,
    cover_image VARCHAR(500),
    cover_bg VARCHAR(50) NOT NULL DEFAULT '#6C3BFF',
    cover_fg VARCHAR(50) NOT NULL DEFAULT '#FFFFFF',
    cover_accent VARCHAR(50) NOT NULL DEFAULT '#FFD23F',
    cover_shape VARCHAR(50) NOT NULL DEFAULT 'circle',
    tag VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_books_slug ON books(slug);
CREATE INDEX IF NOT EXISTS idx_books_category_id ON books(category_id);

-- 4. Book Variants (Paperback / Hardcover / eBook)
CREATE TABLE IF NOT EXISTS book_variants (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    format VARCHAR(50) NOT NULL,
    price_kes INTEGER NOT NULL,
    stock INTEGER NOT NULL DEFAULT 10
);
CREATE INDEX IF NOT EXISTS idx_book_variants_book_id ON book_variants(book_id);

-- 5. Carts
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100) NOT NULL,
    is_gift BOOLEAN NOT NULL DEFAULT FALSE,
    gift_note VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);
CREATE INDEX IF NOT EXISTS idx_carts_session_id ON carts(session_id);

-- 6. Cart Items
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id),
    variant_id INTEGER REFERENCES book_variants(id),
    quantity INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);

-- 7. Orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    reference VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_kes INTEGER NOT NULL,
    delivery_name VARCHAR(120),
    delivery_phone VARCHAR(50),
    delivery_email VARCHAR(255),
    delivery_address TEXT,
    delivery_notes TEXT,
    delivery_fee_kes INTEGER NOT NULL DEFAULT 0,
    is_gift BOOLEAN NOT NULL DEFAULT FALSE,
    gift_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    paid_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_orders_reference ON orders(reference);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);

-- 8. Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id),
    variant_id INTEGER REFERENCES book_variants(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price_kes INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);

-- 9. Payments
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    provider VARCHAR(50) NOT NULL DEFAULT 'paystack',
    reference VARCHAR(100) UNIQUE NOT NULL,
    provider_transaction_id VARCHAR(100),
    channel VARCHAR(50),
    amount_kes INTEGER NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'KES',
    status VARCHAR(50) NOT NULL,
    paid_at TIMESTAMP NOT NULL DEFAULT NOW(),
    raw_response JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_payments_reference ON payments(reference);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);

-- 10. Webhook Events (idempotency tracking)
CREATE TABLE IF NOT EXISTS webhook_events (
    id SERIAL PRIMARY KEY,
    reference VARCHAR(100) UNIQUE NOT NULL,
    payload JSONB,
    received_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_webhook_events_reference ON webhook_events(reference);

-- 11. Newsletter Subscribers
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ============================================
-- SEED DATA
-- ============================================

-- Categories
INSERT INTO categories (name, slug, colour_token) VALUES
    ('Fiction', 'fiction', 'violet'),
    ('Business & Finance', 'business', 'sunshine'),
    ('Kids & Young Readers', 'kids', 'pink'),
    ('Self-growth', 'self-growth', 'mint'),
    ('Romance', 'romance', 'pink')
ON CONFLICT (slug) DO UPDATE SET 
    name = EXCLUDED.name, 
    colour_token = EXCLUDED.colour_token;

-- Books with Rich Summaries and Exact Categorization
INSERT INTO books (title, slug, author, description, category_id, price_kes, stock, cover_image, cover_bg, cover_fg, cover_accent, cover_shape, tag) VALUES
    ('Tomorrow, and Tomorrow, and Tomorrow', 'tomorrow-and-tomorrow-and-tomorrow', 'Gabrielle Zevin',
     'On a bitter-cold day in December, Sam Masur exits a crowded subway car and sees Sadie Green. For a moment, she pretends not to notice him, but then a game begins: a legendary creative partnership that will launch them into video game superstardom.\n\nSpanning thirty years, from Cambridge to Venice Beach, this acclaimed novel explores the intimacies of friendship, artistic passion, grief, and the redemptive power of play. It is an unforgettable ode to connection and identity.',
     (SELECT id FROM categories WHERE slug='fiction'), 1850, 25,
     '/static/img/covers/tomorrow-and-tomorrow-and-tomorrow.jpg', '#6C3BFF', '#FFFFFF', '#FFD23F', 'circle', 'Bestseller'),

    ('Atomic Habits', 'atomic-habits', 'James Clear',
     'No matter your goals, Atomic Habits offers a proven, science-backed framework for improving every day. James Clear reveals how tiny, 1% daily adjustments compound into massive long-term success.\n\nDiscover how to make good habits inevitable and bad habits impossible through the Four Laws of Behavior Change. If you have struggled to sustain routines, the problem is not your willpower—it is your system. An essential manual for mastery and personal growth.',
     (SELECT id FROM categories WHERE slug='self-growth'), 1950, 30,
     '/static/img/covers/atomic-habits.jpg', '#2EC4A0', '#1B1340', '#1B1340', 'arch', 'Staff pick'),

    ('The Psychology of Money', 'the-psychology-of-money', 'Morgan Housel',
     'Doing well with money is not simply about mathematics or financial equations—it is about how you behave. In The Psychology of Money, Morgan Housel shares 19 short, captivating stories exploring the strange ways humans perceive wealth, risk, ego, and happiness.\n\nYou will learn why financial freedom is really about sleeping well at night, how compounding works in the real world, and why keeping money requires humility while making money requires risk. A modern finance classic for every investor.',
     (SELECT id FROM categories WHERE slug='business'), 1650, 20,
     '/static/img/covers/the-psychology-of-money.jpg', '#FFD23F', '#1B1340', '#FF6B35', 'rounded_square', 'Bestseller'),

    ('The Boy, The Mole, The Fox and The Horse', 'the-boy-the-mole-the-fox-and-the-horse', 'Charlie Mackesy',
     'A universal tale of hope, friendship, vulnerability, and gentle wisdom for all ages. Enter the world of four unlikely companions navigating the wild together and asking life''s greatest questions.\n\nAccompanied by Charlie Mackesy''s renowned ink and watercolor illustrations, this book has touched millions of hearts worldwide with its comforting reminder that asking for help is the bravest thing you can do.',
     (SELECT id FROM categories WHERE slug='kids'), 2100, 18,
     '/static/img/covers/the-boy-the-mole-the-fox-and-the-horse.jpg', '#FF8FB1', '#1B1340', '#6C3BFF', 'leaf', 'Kids favourite'),

    ('Yellowface', 'yellowface', 'R.F. Kuang',
     'What is the harm in taking someone else''s story, if you are the one who can tell it? When celebrated author Athena Liu dies in a freak pancake accident, struggling writer June Hayward steals Athena''s finished draft about Chinese laborers in WWI and claims it as her own.\n\nA wildly entertaining, darkly satirical thriller about cultural appropriation, white privilege, literary jealousy, and the relentless pressure of social media stardom.',
     (SELECT id FROM categories WHERE slug='fiction'), 1750, 22,
     '/static/img/covers/yellowface.jpg', '#FFD23F', '#1B1340', '#1B1340', 'arch', 'New'),

    ('Build: An Unorthodox Guide to Making Things Worth Making', 'build-tony-fadell', 'Tony Fadell',
     'Tony Fadell led the teams that created the iPod, the iPhone, and the Nest Learning Thermostat. Build delivers pragmatic mentorship forged across thirty-plus years in Silicon Valley.\n\nFrom handling workplace conflict and choosing startup co-founders to product design principles that thrill customers, this is the definitive playbook for makers, managers, and entrepreneurs.',
     (SELECT id FROM categories WHERE slug='business'), 2250, 14,
     '/static/img/covers/build-tony-fadell.jpg', '#FF6B35', '#1B1340', '#FFFFFF', 'rounded_square', 'Staff pick'),

    ('The Seven Husbands of Evelyn Hugo', 'the-seven-husbands-of-evelyn-hugo', 'Taylor Jenkins Reid',
     'Aging Hollywood movie siren Evelyn Hugo is finally ready to reveal the unfiltered truth about her glamorous, scandalous, and secretive life. She summons unknown journalist Monique Grant to dictate her tell-all biography.\n\nFrom 1950s cinema sets to private tragedies and unforgettable secrets, Evelyn weaves a spellbinding story of ambition, resilience, and an enduring forbidden romance.',
     (SELECT id FROM categories WHERE slug='romance'), 1600, 28,
     '/static/img/covers/the-seven-husbands-of-evelyn-hugo.jpg', '#0E6B56', '#FFFFFF', '#FFD23F', 'leaf', 'Bestseller'),

    ('Big Magic: Creative Living Beyond Fear', 'big-magic', 'Elizabeth Gilbert',
     'Elizabeth Gilbert invites readers to embark on creative journeys free from shame, fear, and perfectionism. In Big Magic, she demystifies the creative process with warmth and generous humor.\n\nWhether you desire to write a book, paint, dance, or start a passion project, this inspiring book unlocks the mystical relationship between human imagination and courage.',
     (SELECT id FROM categories WHERE slug='self-growth'), 1500, 19,
     '/static/img/covers/big-magic.jpg', '#2F6BFF', '#FFFFFF', '#FF8FB1', 'circle', 'New'),

    ('Where the Wild Things Are', 'where-the-wild-things-are', 'Maurice Sendak',
     'When young Max puts on his wolf suit and misbehaves, his mother sends him to bed without supper. Soon, a magical forest sprouts in his bedroom, leading him to a private sailboat that journeys to where the Wild Things roar and dance.\n\nA beloved, Caldecott-winning children''s masterpiece that celebrates boundless imagination, emotional resilience, and the comfort of returning home.',
     (SELECT id FROM categories WHERE slug='kids'), 1350, 16,
     '/static/img/covers/where-the-wild-things-are.jpg', '#2EC4A0', '#1B1340', '#FFD23F', 'arch', 'Kids favourite'),

    ('Book Lovers', 'book-lovers', 'Emily Henry',
     'Nora Stephens is an ambitious New York literary agent who is always the ''villain'' in classic rom-coms. Charlie Lastra is a brooding, hypercritical book editor who knows all of Nora''s secrets.\n\nWhen both end up in the quaint North Carolina village of Sunshine Falls for the summer, their fiery rivalries ignite into a witty, heartfelt love story that defies romantic cliches.',
     (SELECT id FROM categories WHERE slug='romance'), 1700, 25,
     '/static/img/covers/book-lovers.jpg', '#FF8FB1', '#1B1340', '#FFD23F', 'circle', 'New')
ON CONFLICT (slug) DO UPDATE SET
    title = EXCLUDED.title,
    author = EXCLUDED.author,
    description = EXCLUDED.description,
    category_id = EXCLUDED.category_id,
    price_kes = EXCLUDED.price_kes,
    stock = EXCLUDED.stock,
    cover_image = EXCLUDED.cover_image,
    cover_bg = EXCLUDED.cover_bg,
    cover_fg = EXCLUDED.cover_fg,
    cover_accent = EXCLUDED.cover_accent,
    cover_shape = EXCLUDED.cover_shape,
    tag = EXCLUDED.tag;

-- Note: Book formats (Paperback / Hardcover / eBook) are optional and can be added manually in the Admin Dashboard.

-- Demo Users (passwords: secret123 and admin123)
-- These are werkzeug scrypt hashes — they work with Flask-Login's check_password_hash
-- You can also create users through the app's /register page instead.
-- NOTE: If these hashes don't work with your Python/Werkzeug version,
-- just register new accounts through the app UI.
