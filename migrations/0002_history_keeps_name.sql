DELETE FROM usage_history
WHERE id NOT IN (
    SELECT MIN(id) FROM usage_history GROUP BY recipe_id, used_at
);

CREATE TABLE usage_history_next (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER,
    name TEXT NOT NULL DEFAULT '',
    used_at TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE SET NULL
);

INSERT INTO usage_history_next (id, recipe_id, name, used_at)
SELECT usage_history.id, usage_history.recipe_id, recipe.name, usage_history.used_at
FROM usage_history
JOIN recipe ON recipe.id = usage_history.recipe_id;

DROP TABLE usage_history;

ALTER TABLE usage_history_next RENAME TO usage_history;

CREATE UNIQUE INDEX usage_history_recipe_day
ON usage_history (recipe_id, used_at)
WHERE recipe_id IS NOT NULL;
