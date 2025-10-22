-- USERS Table
CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCE Table
CREATE TABLE Produce (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- IMAGES Table
CREATE TABLE Images (
    id INTEGER PRIMARY KEY,
    produce_id INTEGER NOT NULL,
    user_id INTEGER,
    image_path TEXT NOT NULL,
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('pending', 'processing', 'analyzed')) DEFAULT 'pending',
    deleted BOOLEAN DEFAULT 0,
    FOREIGN KEY (produce_id) REFERENCES Produce(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- ANALYSIS RESULTS Table
CREATE TABLE Analysis_Results (
    id INTEGER PRIMARY KEY,
    image_id INTEGER NOT NULL,
    freshness_score INTEGER CHECK(freshness_score BETWEEN 0 AND 100),
    freshness_label TEXT CHECK(freshness_label IN ('good', 'bad')),
    defects_detected TEXT, -- Store JSON string
    confidence_score FLOAT CHECK(confidence_score BETWEEN 0.0 AND 1.0),
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES Images(id)
);
