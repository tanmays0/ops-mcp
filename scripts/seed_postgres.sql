CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price_cents INT NOT NULL CHECK (price_cents >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users (id),
    total_cents INT NOT NULL CHECK (total_cents >= 0),
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO users (email, created_at) VALUES
    ('alice@example.com', NOW() - INTERVAL '10 days'),
    ('bob@example.com', NOW() - INTERVAL '5 days'),
    ('carol@example.com', NOW() - INTERVAL '1 day')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (sku, name, price_cents) VALUES
    ('WIDGET-1', 'Blue Widget', 1999),
    ('WIDGET-2', 'Red Widget', 2499),
    ('GADGET-9', 'Pro Gadget', 9999)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO orders (user_id, total_cents, status, created_at)
SELECT u.id, v.total_cents, v.status, v.created_at
FROM (
    VALUES
        ('alice@example.com', 1999, 'paid', NOW() - INTERVAL '3 days'),
        ('alice@example.com', 9999, 'paid', NOW() - INTERVAL '2 days'),
        ('bob@example.com', 2499, 'pending', NOW() - INTERVAL '1 day'),
        ('bob@example.com', 1999, 'paid', NOW() - INTERVAL '12 hours'),
        ('carol@example.com', 4498, 'paid', NOW() - INTERVAL '6 hours')
) AS v(email, total_cents, status, created_at)
JOIN users u ON u.email = v.email
WHERE NOT EXISTS (SELECT 1 FROM orders LIMIT 1);
