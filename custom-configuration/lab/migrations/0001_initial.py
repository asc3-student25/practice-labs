"""Initial schema: users table."""


def upgrade():
    return [
        "CREATE TABLE users ("
        "id INTEGER PRIMARY KEY, "
        "username TEXT NOT NULL"
        ")"
    ]


def downgrade():
    return ["DROP TABLE users"]
