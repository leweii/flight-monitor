-- Price records table
CREATE TABLE IF NOT EXISTS price_records (
    id SERIAL PRIMARY KEY,
    origin CHAR(3) NOT NULL,
    destination CHAR(3) NOT NULL,
    departure_date DATE NOT NULL,
    source VARCHAR(20) NOT NULL,
    airline VARCHAR(50),
    price DECIMAL(10,2) NOT NULL,
    currency CHAR(3) DEFAULT 'CNY',
    flight_number VARCHAR(20),
    stops INT DEFAULT 0,
    fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_route_date ON price_records(origin, destination, departure_date);
CREATE INDEX IF NOT EXISTS idx_fetched_at ON price_records(fetched_at);

-- Alert logs table
CREATE TABLE IF NOT EXISTS alert_logs (
    id SERIAL PRIMARY KEY,
    route_name VARCHAR(100),
    origin CHAR(3),
    destination CHAR(3),
    departure_date DATE,
    trigger_type VARCHAR(20),
    trigger_condition TEXT,
    price DECIMAL(10,2),
    notified_via TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
