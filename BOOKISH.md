# Bookish — Project Spec

An online bookstore built with **Flask (Python)**. Bright, bubbly, attention-grabbing UI. Payments through **Paystack**. An order is only marked paid, and the payment only logged in the database, **after Paystack confirms it server-side**.

> The five UI screens (home, mobile home, shop, product, cart) and the wordmark board are on the design canvas "Bookish Store". Book titles, authors and prices in the designs are sample content only.

---

## 1. Tech stack

| Layer | Choice |
|---|---|
| Backend | Flask 3, Python 3.11+ |
| Templates | Jinja2, plain CSS (or Tailwind if preferred), a little vanilla JS |
| Database | PostgreSQL in production, SQLite for local dev (SQLAlchemy + Flask-Migrate) |
| Auth | Flask-Login (email + password, hashed with Werkzeug) |
| Payments | Paystack (Transaction Initialize, Verify, Webhook) |
| HTTP client | `requests` |
| Config | `.env` via `python-dotenv` |
| Server | Gunicorn behind Nginx (or any PaaS) |

---

## 2. Design system

### 2.1 Colours

| Token | Hex | Use |
|---|---|---|
| ink | `#1B1340` | text, outlines, dark sections, footer |
| violet | `#6C3BFF` | hero, summary card, primary accents |
| tangerine | `#FF6B35` | main buttons, cart button, add-to-cart |
| sunshine | `#FFD23F` | announcement bar, highlights, active nav pill |
| mint | `#2EC4A0` | accents, "Gift ready" card, self-growth tile |
| pink | `#FF8FB1` | accents, kids tile, shop banner |
| blue | `#2F6BFF` | extra book cover colour |
| forest | `#0E6B56` | extra book cover colour |
| cream | `#FFF7E8` | page background |
| white | `#FFFFFF` | cards, inputs |
| muted | `#5B5480` | secondary text (author names, captions) |
| lavender-text | `#EDE6FF` | body text on violet |

Rules:
- Text on tangerine, sunshine, mint and pink is **ink**. Text on violet and ink is **white/cream**. White on tangerine fails contrast, so don't use it.
- Every card, button and input has a **2px ink border**.
- Primary buttons also get a hard offset shadow: `box-shadow: 4px 4px 0 #1B1340`.

### 2.2 Typography

- **Display / headings / book titles:** Fraunces, weights 600 and 800, tight letter spacing (`-0.02em` to `-0.03em`).
- **Body / UI:** DM Sans, weights 400, 500 and 700.
- **Wordmark only:** Fredoka, weight 700.
- Load all three from Google Fonts.

| Element | Size |
|---|---|
| Hero headline | 88px / line-height 1 (46px on mobile) |
| Section heading | 48px |
| Page title (Shop, Cart) | 72–80px |
| Product title | 68px |
| Card title | 22px Fraunces 800 |
| Body | 16–20px |
| Small labels | 12–14px, uppercase, `letter-spacing: 0.1em` |

### 2.3 Shape and spacing

- Pill buttons and chips: `border-radius: 999px`.
- Cards: 28–40px radius. Hero and promo blocks: 36–40px.
- Book covers: `8px 18px 18px 8px` (spine side squarer).
- Page side padding: 64px on desktop, 16px on mobile.
- Section gaps: 88–96px between big sections on desktop.
- Touch targets are at least 44px (icon buttons are 44–48px).

### 2.4 Wordmark ("bookish")

- Lower-case, **Fredoka Bold**, letter-spacing `0.1em`.
- Seven letters, each a different fill and a slight tilt:

| Letter | Fill | Rotate | Offset Y |
|---|---|---|---|
| b | violet `#6C3BFF` | -6° | +0.03em |
| o | tangerine `#FF6B35` | +5° | -0.05em |
| o | sunshine `#FFD23F` | -4° | +0.04em |
| k | mint `#2EC4A0` | +6° | -0.03em |
| i | pink `#FF8FB1` | -5° | +0.03em |
| s | violet `#6C3BFF` | +5° | -0.05em |
| h | tangerine `#FF6B35` | -4° | +0.03em |

- Thick outline using `-webkit-text-stroke: 0.17em currentColor` with `paint-order: stroke fill`, plus a drop shadow `text-shadow: 0 0.08em 0 currentColor`.
- The outline uses `currentColor`: **ink on light backgrounds, cream on dark or violet backgrounds**.
- Two small white "bubbles" (circles with a currentColor border) float off the end: one `0.34em`, one `0.18em`.
- Sizes: 40px in desktop header and footer, 30px on mobile.
- Next to it sits the logo mark: a 44px violet rounded square (radius 14px, rotated -6°) with a yellow open-book line icon.
- The round "b" app icon / favicon: a single bubble "b" on a 130px circle (violet, yellow or pink background).
- Best done as an **SVG file** for production so it renders the same everywhere (`paint-order` stroke is well supported, but SVG is safer for favicons and emails).

### 2.5 Book cover component (CSS-drawn placeholder)

Until real cover images are uploaded, covers are drawn in CSS:
- Aspect ratio 2:3, padding 24–26px, flex column, space-between.
- Title at top in Fraunces 800 (about 32px on grid cards).
- A geometric shape bottom-right (46% of the width): circle, arch (`100px 100px 0 0`), rounded square, or leaf (`50% 0 50% 0`).
- Background, text and shape colours chosen per book from the palette.
- Soft shadow `0 14px 28px rgba(27,19,64,0.18)`.
- In production: if `book.cover_image` exists show the image with the same radius and shadow, else fall back to this generated cover.

### 2.6 Icons

Inline stroke SVG, 2px stroke, round caps. Needed: search, heart, user, bag, plus, arrow-right, home, book, truck, card, gift.

### 2.7 Accessibility

- Real `<button>`, `<a>`, `<input>` with labels or `aria-label` (icon-only buttons always get one).
- Text contrast is at least 4.5:1.
- Wordmark spans are `aria-hidden`; wrapper has `role="img" aria-label="bookish"`.
- Every page works at phone width (no horizontal scroll).

---

## 3. Screens and UI details

### 3.1 Global header (all desktop pages)

1. **Announcement bar**, sunshine background, centred bold 14px text.
2. **Header row** (padding 20px 64px, wraps on small screens):
   - Left: logo mark + wordmark, links home.
   - Centre: nav pills (Shop, New in, Bestsellers, Kids, Offers). Active page gets a sunshine pill.
   - Right: search pill (white, 2px ink border, 48px tall, min-width 240px), wishlist circle, account circle, and cart circle (tangerine) with an ink count badge (yellow number) at the top-right.

### 3.2 Home

1. **Hero** (violet panel, radius 40px, padding 72px 64px):
   - Left: yellow pill label "New season reads", headline "Find your next **favourite** read." (the word "favourite" on a tilted yellow highlight), short supporting paragraph, two buttons: tangerine "Shop books" with arrow, outlined white "Browse genres".
   - Right: three tilted book covers (orange, yellow, mint) overlapping, plus a round pink "Gift a story" sticker at the top-right.
2. **Shop by shelf**: four coloured tiles (Fiction violet, Business yellow, Kids pink, Self-growth mint), 300px tall, big Fraunces word, a decorative shape peeking from the top-right corner, small uppercase caption.
3. **Fresh off the shelf**: row of four book cards (see 3.4).
4. **Promo band**: two large cards side by side: tangerine "Bundle deal — Read more, spend less." and mint "Gift ready — Give a story they'll keep." Each has a dark pill label and an ink button.
5. **Perks row**: three items with round icon badges: "Pay your way" (card/M-Pesa via Paystack), "Delivered to you", "Gift wrapping".
6. **Newsletter**: sunshine panel, headline "Get book news, first.", email input and an ink "Sign me up" button.
7. **Footer** (ink): wordmark with cream outline, tagline, columns Shop / Help / Follow, copyright line.

### 3.3 Mobile home (390px wide)

- Announcement, compact header (wordmark 30px, wishlist, cart with badge), full-width search.
- Violet hero card with a smaller headline (46px), one tangerine button, three small tilted covers.
- "Shop by shelf" as a horizontally scrolling row of coloured pills.
- "Fresh off the shelf" as a **2-column grid**.
- Tangerine bundle card.
- **Bottom tab bar** (ink): Home, Shop, Saved, Account. Active tab is yellow.

### 3.4 Shop (catalog)

- Pink banner with breadcrumb "Home / Shop", 80px "The shop" title, and decorative shapes.
- **Filter row**: genre chips (All, Fiction, Business, Kids, Self-growth, Romance), each in its own palette colour; the selected chip is ink with white text. On the right: result count and a "Sort by" select (Newest, Price low to high, Price high to low).
- **Grid** of book cards, 4 per row on desktop, wraps down to 1 on phones.
- **Book card**: cover (links to product), small outlined tag pill (New, Bestseller, Staff pick, Kids favourite), title (Fraunces 22px), author (muted), price (bold 20px), round tangerine **add-to-cart** button (48px, plus icon).
- Pagination: numbered circles (current one violet), "Next page" yellow pill.

### 3.5 Product page

- Breadcrumb.
- **Left:** yellow panel with decorative pink circle and mint tilted square; large violet cover (max 380px wide) tilted -3° with a strong shadow.
- **Right:**
  - Pink "New" tag, 68px title, "by Author" link in violet.
  - Short description (18px, 1.6 line height).
  - **Format selector**: three toggle cards (Paperback, Hardcover, eBook), each showing its price. Selected = violet with white text, with `aria-pressed`.
  - **Quantity stepper** (− / number / +, min 1, max 9) and live **total** in 40px Fraunces.
  - Tangerine **Add to cart** button, plus a round wishlist button.
  - Dashed divider, then three small bullet perks (pay with M-Pesa or card, delivered to your door, gift wrapping).
- **More like this**: four smaller covers with title, author, price.
- In the real build, formats map to variants (`book_variants` table) so each format has its own price and stock.

### 3.6 Cart and checkout

- Title "Your cart" with a tilted yellow "N books" badge.
- **Left column:** a white card per line item: small cover (104×156), title link, "author · format", quantity stepper, "Remove" text button, line price on the right. Below the items: a mint "Make it a gift" card (gift-wrap option) and a "Keep browsing" link.
- **Right column:** violet **Order summary** card:
  - Subtotal, Delivery (calculated at checkout), a dashed rule, and Total in large yellow Fraunces.
  - **Pay with** selector. In the first design this showed M-Pesa and Card tabs plus an M-Pesa phone field. **With Paystack, this block changes**:
    - Remove the phone-number field and the M-Pesa/Card tabs. Paystack's checkout shows the available channels (card, mobile money/M-Pesa where enabled on your account) and collects the phone number itself.
    - Replace them with a single tangerine button, **"Pay securely with Paystack"**, plus a small line: "You'll choose M-Pesa or card on the next step."
    - Keep the customer's **email field** (Paystack requires an email) pre-filled from their account.
  - States the button needs: default, loading (spinner, disabled), error banner (inline, above the button).

### 3.7 Extra screens to add (not yet designed)

| Screen | Notes |
|---|---|
| Delivery details | name, phone, county/town, street/building, notes (before payment) |
| Payment result: success | confetti-style bubbles, order number, summary, "Continue shopping" |
| Payment result: failed/cancelled | friendly message, "Try again" button that re-opens payment for the same order |
| Orders list and detail | status chip (pending, paid, shipped, delivered, cancelled), items, payment reference |
| Login / register | same card style, 2px borders |
| Admin: books, orders | simple tables; later |

---

## 4. Payments with Paystack

### 4.1 Principles

1. **Never trust the browser.** The redirect back to your site only means "the customer came back". An order becomes paid only after your **server verifies the transaction with Paystack**.
2. **The server decides the amount.** Compute the total from the database, never from form fields.
3. **Verify before logging.** The `payments` row and the `paid` order status are written only when Paystack reports `status == "success"` and the amount and currency match.
4. **Idempotent.** The callback and the webhook can both arrive (and arrive twice). Processing the same reference twice must not double-pay, double-decrement stock, or double-email.
5. **Secret key stays on the server.** Only the public key (if you use the popup) may reach the browser.

### 4.2 Flow

```
Customer clicks "Pay securely with Paystack"
   │
   ▼
[Flask] POST /checkout/pay
   1. Load cart, validate stock, compute total (KES) on the server
   2. Create order with status = "pending" and a unique reference
      (the order row is only the record of what is being bought; it is NOT a payment)
   3. Call Paystack: POST /transaction/initialize
        email, amount (KES x 100), currency "KES",
        reference, callback_url, metadata { order_id }
   4. Redirect the customer to data.authorization_url
   │
   ▼
Customer pays on Paystack (card or M-Pesa / mobile money)
   │
   ├────────────► Paystack redirects to  GET /payment/callback?reference=...
   │                 [Flask] verify_and_complete(reference)
   │
   └────────────► Paystack sends webhook  POST /webhooks/paystack  (event charge.success)
                     [Flask] check signature, then verify_and_complete(reference)

verify_and_complete(reference):
   1. Look up the order by reference. If it is already "paid", stop (idempotent).
   2. Call Paystack: GET /transaction/verify/:reference
   3. Confirm ALL of:
        data.status == "success"
        data.amount == order.total_kes * 100
        data.currency == "KES"
        data.reference == order.reference
   4. In ONE database transaction:
        insert into payments (...)          ← the payment is logged here, after confirmation
        update orders set status = "paid", paid_at = now()
        decrement stock for each order item
        clear the user's cart
   5. Commit. Send confirmation email. Show the success page.
   If status is "failed" or "abandoned": mark order "payment_failed" (optional log), show the failed page.
```

The callback and webhook both call `verify_and_complete`. The callback gives the customer an instant result; the webhook is the safety net when the customer closes the tab before returning.

### 4.3 Paystack endpoints used

| Purpose | Request |
|---|---|
| Initialize | `POST https://api.paystack.co/transaction/initialize` |
| Verify | `GET https://api.paystack.co/transaction/verify/:reference` |
| Webhook (incoming) | your `POST /webhooks/paystack` |

All calls use the header `Authorization: Bearer <PAYSTACK_SECRET_KEY>`.

- **Amount** is in the smallest currency unit: **KES 1,450 → `145000`**.
- **Currency:** `KES`.
- **Channels:** leave unset to show whatever your Paystack account has enabled, or set `channels` explicitly (e.g. `["card", "mobile_money"]`). Confirm which channels and M-Pesa options are active for your account in the Paystack dashboard before launch, and test each one.
- **Reference:** generate your own, unique per attempt (e.g. `BK-<order_id>-<random>`), so retrying a failed payment makes a new reference.

### 4.4 Webhook security

- Paystack signs each webhook with the header `x-paystack-signature`: an **HMAC-SHA512 of the raw request body** using your secret key.
- Compute it yourself on the **raw bytes** (`request.get_data()`), compare with `hmac.compare_digest`, and reject mismatches with 401.
- Return **HTTP 200 quickly**. Do slow work (emails) after the response or in a background job.
- Store each processed event id/reference in `webhook_events` to ignore duplicates.
- Set the webhook URL and callback URL in the Paystack dashboard (HTTPS required in production; use a tunnel like ngrok for local testing).
- Webhooks are not authenticated by IP alone; still verify the signature.

### 4.5 Reference code (Flask)

`app/payments/paystack.py`

```python
import hmac, hashlib, secrets
import requests
from flask import current_app

BASE = "https://api.paystack.co"

def _headers():
    return {
        "Authorization": f"Bearer {current_app.config['PAYSTACK_SECRET_KEY']}",
        "Content-Type": "application/json",
    }

def new_reference(order_id: int) -> str:
    return f"BK-{order_id}-{secrets.token_hex(6)}"

def initialize(email, amount_kes, reference, callback_url, metadata):
    payload = {
        "email": email,
        "amount": int(amount_kes * 100),   # KES -> subunit
        "currency": "KES",
        "reference": reference,
        "callback_url": callback_url,
        "metadata": metadata,
    }
    r = requests.post(f"{BASE}/transaction/initialize",
                      json=payload, headers=_headers(), timeout=15)
    r.raise_for_status()
    body = r.json()
    if not body.get("status"):
        raise RuntimeError(body.get("message", "Paystack initialize failed"))
    return body["data"]   # authorization_url, access_code, reference

def verify(reference):
    r = requests.get(f"{BASE}/transaction/verify/{reference}",
                     headers=_headers(), timeout=15)
    r.raise_for_status()
    body = r.json()
    if not body.get("status"):
        raise RuntimeError(body.get("message", "Paystack verify failed"))
    return body["data"]

def valid_signature(raw_body: bytes, signature: str) -> bool:
    key = current_app.config["PAYSTACK_SECRET_KEY"].encode()
    expected = hmac.new(key, raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature or "")
```

`app/payments/service.py`

```python
from datetime import datetime, timezone
from app.extensions import db
from app.models import Order, Payment, Book
from app.payments import paystack

def verify_and_complete(reference: str) -> str:
    """Returns 'paid', 'failed' or 'unknown'. Safe to call many times."""
    order = Order.query.filter_by(reference=reference).with_for_update().first()
    if order is None:
        return "unknown"
    if order.status == "paid":
        return "paid"                       # already done (callback + webhook race)

    data = paystack.verify(reference)

    ok = (
        data.get("status") == "success"
        and data.get("currency") == "KES"
        and int(data.get("amount", 0)) == order.total_kes * 100
        and data.get("reference") == order.reference
    )
    if not ok:
        if data.get("status") in ("failed", "abandoned"):
            order.status = "payment_failed"
            db.session.commit()
            return "failed"
        return "failed"

    # confirmed -> now log it, in one transaction
    db.session.add(Payment(
        order_id=order.id,
        provider="paystack",
        reference=reference,
        provider_transaction_id=str(data.get("id")),
        channel=data.get("channel"),
        amount_kes=order.total_kes,
        currency="KES",
        status="success",
        paid_at=datetime.now(timezone.utc),
        raw_response=data,                  # JSON column, keep for audits
    ))
    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    for item in order.items:
        item.book.stock = max(0, item.book.stock - item.quantity)
    db.session.commit()
    return "paid"
```

`app/payments/routes.py`

```python
from flask import Blueprint, request, redirect, url_for, render_template, abort, current_app
from flask_login import login_required, current_user
from app.cart import cart_lines, cart_total_kes, clear_cart
from app.extensions import db
from app.models import Order, OrderItem, WebhookEvent
from app.payments import paystack
from app.payments.service import verify_and_complete

bp = Blueprint("payments", __name__)

@bp.post("/checkout/pay")
@login_required
def pay():
    lines = cart_lines()
    if not lines:
        return redirect(url_for("cart.view"))
    order = Order(user_id=current_user.id, status="pending",
                  total_kes=cart_total_kes(lines))        # server-computed
    db.session.add(order); db.session.flush()
    for l in lines:
        db.session.add(OrderItem(order_id=order.id, book_id=l.book.id,
                                 quantity=l.qty, unit_price_kes=l.unit_price))
    order.reference = paystack.new_reference(order.id)
    db.session.commit()

    data = paystack.initialize(
        email=current_user.email,
        amount_kes=order.total_kes,
        reference=order.reference,
        callback_url=url_for("payments.callback", _external=True),
        metadata={"order_id": order.id},
    )
    return redirect(data["authorization_url"])

@bp.get("/payment/callback")
@login_required
def callback():
    reference = request.args.get("reference") or request.args.get("trxref")
    if not reference:
        abort(400)
    result = verify_and_complete(reference)
    if result == "paid":
        clear_cart()
        return render_template("payment_success.html", reference=reference)
    return render_template("payment_failed.html", reference=reference)

@bp.post("/webhooks/paystack")
def webhook():
    raw = request.get_data()
    if not paystack.valid_signature(raw, request.headers.get("x-paystack-signature")):
        abort(401)
    event = request.get_json(silent=True) or {}
    if event.get("event") == "charge.success":
        ref = event["data"]["reference"]
        if not WebhookEvent.seen(ref):                    # idempotency guard
            WebhookEvent.record(ref, event)
            verify_and_complete(ref)
    return "", 200
```

Notes:
- Exempt the webhook route from CSRF protection if you use Flask-WTF (it is called by Paystack, not a browser form).
- `with_for_update()` plus the `status == "paid"` check is what stops a callback and a webhook from both completing the same order. (On SQLite it is ignored; rely on Postgres in production.)
- Never skip the amount check. It stops someone tampering with a cheaper order and paying for that.

### 4.6 Testing checklist

- Use **Paystack test keys** (`sk_test_...`, `pk_test_...`) and test cards/numbers from the Paystack docs.
- Success path: order ends `paid`, exactly one `payments` row, stock decremented once, cart cleared.
- Customer closes the tab after paying: webhook still marks the order paid.
- Callback and webhook arriving together: still only one payment row.
- Tampered amount / wrong currency / wrong reference: order stays unpaid.
- Failed or abandoned payment: order is `payment_failed`, "Try again" creates a new reference.
- Invalid webhook signature: 401, nothing changes.
- Paystack API down or timing out: customer sees a friendly error, nothing is marked paid; a retry or the webhook can complete it later.

---

## 5. Database schema

```sql
users (
  id, name, email UNIQUE, phone, password_hash, is_admin BOOL DEFAULT false, created_at
)

categories (id, name, slug UNIQUE, colour_token)        -- Fiction, Business, Kids, ...

books (
  id, title, slug UNIQUE, author, description,
  category_id → categories,
  price_kes INT,                 -- whole shillings
  stock INT,
  cover_image NULL,              -- falls back to generated CSS cover
  cover_bg, cover_fg, cover_accent, cover_shape,   -- for the generated cover
  tag NULL,                      -- New / Bestseller / Staff pick
  is_active BOOL, created_at
)

book_variants (                  -- optional: paperback / hardcover / eBook
  id, book_id → books, format, price_kes, stock
)

carts (id, user_id NULL, session_id, created_at)        -- guests use session_id
cart_items (id, cart_id → carts, book_id → books, variant_id NULL, quantity)

orders (
  id, user_id → users,
  reference UNIQUE,              -- sent to Paystack
  status,                        -- pending | paid | payment_failed | shipped | delivered | cancelled
  total_kes INT,                 -- computed server-side
  delivery_name, delivery_phone, delivery_address, delivery_notes,
  is_gift BOOL, gift_note,
  created_at, paid_at NULL
)

order_items (
  id, order_id → orders, book_id → books, variant_id NULL,
  quantity, unit_price_kes      -- price frozen at purchase time
)

payments (                       -- written ONLY after Paystack confirms success
  id, order_id → orders,
  provider DEFAULT 'paystack',
  reference UNIQUE,
  provider_transaction_id,
  channel,                       -- card / mobile_money / ...
  amount_kes, currency,
  status,                        -- 'success'
  paid_at,
  raw_response JSON,             -- full verify payload for audits and disputes
  created_at
)

webhook_events (id, reference UNIQUE, payload JSON, received_at)   -- idempotency log

newsletter_subscribers (id, email UNIQUE, created_at)
```

Indexes: `orders.reference`, `orders.user_id`, `payments.reference`, `books.slug`, `books.category_id`.

Money is stored as **integer KES** (no floats). Convert to subunits (×100) only when talking to Paystack.

---

## 6. Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Home |
| GET | `/shop` | Catalog (query: `genre`, `sort`, `q`, `page`) |
| GET | `/book/<slug>` | Product page |
| POST | `/cart/add` | Add item (book, variant, qty) |
| POST | `/cart/update` | Change quantity |
| POST | `/cart/remove` | Remove item |
| GET | `/cart` | Cart view |
| GET/POST | `/checkout/details` | Delivery details |
| POST | `/checkout/pay` | Create pending order, initialize Paystack, redirect |
| GET | `/payment/callback` | Customer returns; verify then show result |
| POST | `/webhooks/paystack` | Paystack webhook (signature checked) |
| GET | `/orders` · `/orders/<id>` | Order history and detail |
| GET/POST | `/login` · `/register` · POST `/logout` | Auth |
| POST | `/newsletter` | Subscribe |
| GET | `/admin/...` | Manage books and orders (later) |

---

## 7. Project structure

```
bookish/
├─ app/
│  ├─ __init__.py            # create_app()
│  ├─ config.py
│  ├─ extensions.py          # db, migrate, login_manager, csrf
│  ├─ models.py
│  ├─ catalog/               # home, shop, product routes
│  ├─ cart/                  # cart logic and routes
│  ├─ auth/
│  ├─ orders/
│  ├─ payments/
│  │   ├─ paystack.py        # API client + signature check
│  │   ├─ service.py         # verify_and_complete
│  │   └─ routes.py          # pay, callback, webhook
│  ├─ templates/
│  │   ├─ base.html          # announcement bar, header, footer
│  │   ├─ partials/          # wordmark.html, book_card.html, icons.html
│  │   ├─ home.html  shop.html  product.html  cart.html
│  │   ├─ checkout_details.html  payment_success.html  payment_failed.html
│  │   └─ orders/ ...
│  └─ static/
│      ├─ css/  (tokens.css, base.css, components.css)
│      ├─ js/   (cart.js, product.js)
│      └─ img/  (logo.svg, favicon.svg)
├─ migrations/
├─ tests/
├─ .env.example
├─ requirements.txt
└─ wsgi.py
```

Put the design tokens in `tokens.css` as CSS variables (`--ink`, `--violet`, `--tangerine`, ...) and reuse them everywhere. Build `wordmark.html` and `book_card.html` as Jinja partials so every page uses the same markup.

---

## 8. Configuration

`.env.example`

```
FLASK_ENV=development
SECRET_KEY=change-me
DATABASE_URL=postgresql://user:pass@localhost/bookish

PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
SITE_URL=https://your-domain.example      # used to build callback URLs
```

`requirements.txt` (starting point)

```
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-WTF
python-dotenv
requests
psycopg2-binary
gunicorn
```

---

## 9. Security and quality

- Hash passwords (Werkzeug), session cookies `HttpOnly`, `Secure`, `SameSite=Lax`.
- CSRF protection on all forms (except the Paystack webhook, which is signature-verified).
- Server-side validation of quantities, stock and prices; never trust client totals.
- Secret keys only in environment variables, never in git or templates.
- Log payment events (reference, order id, result) but never log full card data (you never receive it with Paystack-hosted checkout).
- Rate-limit login and the pay route.
- HTTPS everywhere in production.
- Keep the raw Paystack verify response in `payments.raw_response` for refunds and disputes.

---

## 10. Build order

1. Project skeleton, config, models, migrations; seed categories and sample books.
2. `tokens.css`, base layout (header, footer, wordmark), home page.
3. Shop (filters, sort, pagination) and product page.
4. Cart (session-based) and cart page.
5. Auth, delivery details, orders.
6. **Paystack**: initialize, callback verify, webhook, success/failed pages, with tests (section 4.6).
7. Emails (order confirmation), admin screens, polish and accessibility pass.
8. Switch to live Paystack keys only after test-mode runs pass end to end.

---

## 11. Open decisions

- Delivery fees: flat, by county, or free over a threshold? (Cart currently shows "At checkout".)
- Guest checkout vs login required. (Paystack needs an email either way.)
- Real cover images vs generated CSS covers.
- Which Paystack channels to enable (card only, or card + M-Pesa/mobile money) on your account.
- Bundle-deal rules ("pick any three paperbacks") and gift-wrap price.
- Newsletter provider.
