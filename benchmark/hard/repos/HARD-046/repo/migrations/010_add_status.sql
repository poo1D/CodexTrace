ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'new';
UPDATE users SET status = 'active' WHERE name = 'Ada';
