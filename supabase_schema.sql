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
    ('Self-Help', 'self-help', 'sunshine'),
    ('Fiction', 'fiction', 'violet'),
    ('Business', 'business', 'mint'),
    ('Kids', 'kids', 'pink'),
    ('Science', 'science', 'violet')
ON CONFLICT (slug) DO NOTHING;

-- Books
INSERT INTO books (title, slug, author, description, category_id, price_kes, stock, cover_image, cover_bg, cover_fg, cover_accent, cover_shape, tag) VALUES
    ('The Psychology of Money', 'the-psychology-of-money', 'Morgan Housel',
     'Timeless lessons on wealth, greed, and happiness. Morgan Housel shares 19 short stories exploring the strange ways people think about money.',
     (SELECT id FROM categories WHERE slug='self-help'), 1500, 25,
     '/static/img/covers/the-psychology-of-money.jpg', '#1B1340', '#FFFFFF', '#FFD23F', 'circle', 'Bestseller'),

    ('Atomic Habits', 'atomic-habits', 'James Clear',
     'An easy and proven way to build good habits and break bad ones. Learn how tiny changes can lead to remarkable results.',
     (SELECT id FROM categories WHERE slug='self-help'), 1400, 30,
     '/static/img/covers/atomic-habits.jpg', '#FFD23F', '#1B1340', '#FF6B35', 'rounded_square', 'Staff pick'),

    ('Tomorrow, and Tomorrow, and Tomorrow', 'tomorrow-and-tomorrow-and-tomorrow', 'Gabrielle Zevin',
     'Two friends find their way back to each other and forge a bond that will forever be changed by the creative partnership that follows.',
     (SELECT id FROM categories WHERE slug='fiction'), 1650, 15,
     '/static/img/covers/tomorrow-and-tomorrow-and-tomorrow.jpg', '#6C3BFF', '#FFFFFF', '#3ECFB4', 'arch', 'New'),

    ('Rich Dad Poor Dad', 'rich-dad-poor-dad', 'Robert T. Kiyosaki',
     'What the rich teach their kids about money that the poor and middle class do not! A personal finance classic.',
     (SELECT id FROM categories WHERE slug='business'), 1200, 40,
     '/static/img/covers/rich-dad-poor-dad.jpg', '#3ECFB4', '#1B1340', '#FFD23F', 'leaf', 'Bestseller'),

    ('The Very Hungry Caterpillar', 'the-very-hungry-caterpillar', 'Eric Carle',
     'The all-time classic picture book, from generation to generation. A caterpillar eats his way through a week of food.',
     (SELECT id FROM categories WHERE slug='kids'), 850, 50,
     '/static/img/covers/the-very-hungry-caterpillar.jpg', '#FF6B9D', '#1B1340', '#3ECFB4', 'circle', 'Kids favourite'),

    ('Thinking, Fast and Slow', 'thinking-fast-and-slow', 'Daniel Kahneman',
     'A groundbreaking tour of the mind that explains the two systems that drive the way we think — System 1 (fast) and System 2 (slow).',
     (SELECT id FROM categories WHERE slug='science'), 1800, 20,
     '/static/img/covers/thinking-fast-and-slow.jpg', '#1B1340', '#FFFFFF', '#6C3BFF', 'rounded_square', NULL),

    ('Where the Wild Things Are', 'where-the-wild-things-are', 'Maurice Sendak',
     'Max sails to the land of the Wild Things, where he becomes their king. A beloved children''s classic.',
     (SELECT id FROM categories WHERE slug='kids'), 950, 35,
     '/static/img/covers/where-the-wild-things-are.jpg', '#FF6B35', '#FFFFFF', '#FFD23F', 'arch', 'New'),

    ('Sapiens: A Brief History of Humankind', 'sapiens', 'Yuval Noah Harari',
     'A narrative of humanity''s creation and evolution. How did our species succeed in the battle for dominance?',
     (SELECT id FROM categories WHERE slug='science'), 1700, 18,
     '/static/img/covers/sapiens.jpg', '#6C3BFF', '#FFFFFF', '#FF6B35', 'circle', 'Staff pick'),

    ('The Lean Startup', 'the-lean-startup', 'Eric Ries',
     'How today''s entrepreneurs use continuous innovation to create radically successful businesses.',
     (SELECT id FROM categories WHERE slug='business'), 1350, 22,
     '/static/img/covers/the-lean-startup.jpg', '#3ECFB4', '#1B1340', '#1B1340', 'leaf', NULL),

    ('Dune', 'dune', 'Frank Herbert',
     'Set on the desert planet Arrakis, Dune is the story of Paul Atreides and his family''s fight for control of the most valuable resource in the universe.',
     (SELECT id FROM categories WHERE slug='fiction'), 1550, 28,
     '/static/img/covers/dune.jpg', '#FFD23F', '#1B1340', '#FF6B35', 'rounded_square', 'Bestseller')
ON CONFLICT (slug) DO NOTHING;

-- Book Variants (Paperback / Hardcover / eBook for each book)
DO $$
DECLARE
    book_rec RECORD;
BEGIN
    FOR book_rec IN SELECT id, price_kes FROM books LOOP
        INSERT INTO book_variants (book_id, format, price_kes, stock) VALUES
            (book_rec.id, 'Paperback', book_rec.price_kes, 20),
            (book_rec.id, 'Hardcover', book_rec.price_kes + 400, 10),
            (book_rec.id, 'eBook', GREATEST(book_rec.price_kes - 300, 500), 999)
        ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- Demo Users (passwords: secret123 and admin123)
-- These are werkzeug scrypt hashes — they work with Flask-Login's check_password_hash
-- You can also create users through the app's /register page instead.
-- NOTE: If these hashes don't work with your Python/Werkzeug version,
-- just register new accounts through the app UI.
