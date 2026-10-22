CREATE TABLE recipe (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    note TEXT NOT NULL DEFAULT '',
    last_used TEXT
);

CREATE TABLE usage_history (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL,
    used_at TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE CASCADE
);
