-- NOTE: schema fields are sorted for predictability

CREATE TABLE IF NOT EXISTS bank
(
    account_id     TEXT,
    amount         REAL,
    c1             TEXT,
    c2             TEXT,
    c3             TEXT,
    date           TEXT,
    inc_or_exp     TEXT,
    name           TEXT,
    transaction_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS location
(
    address        TEXT,
    city           TEXT,
    lat            REAL,
    lon            REAL,
    state          TEXT,
    store_number   INTEGER,
    transaction_id TEXT PRIMARY KEY,
    zip            INTEGER
);

CREATE TABLE IF NOT EXISTS payment_meta
(
    by_order_of       TEXT,
    payee             TEXT,
    payer             TEXT,
    payment_method    TEXT,
    payment_processor TEXT,
    reference_number  TEXT,
    ppd_id            INTEGER,
    reason            TEXT,
    transaction_id    TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS plot_cache
(
    end_date    TEXT,
    full_title  TEXT,
    html        TEXT,
    lookup_date TEXT,
    start_date  TEXT,
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (full_title, start_date, end_date, lookup_date)
);
