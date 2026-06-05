"""Add email column to users."""


def upgrade():
    return ["ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''"]


def downgrade():
    return ["ALTER TABLE users DROP COLUMN email"]
