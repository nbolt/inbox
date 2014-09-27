"""add_namespace_to_calendars

Revision ID: 4015edc83ba
Revises:4d10bc835f44
Create Date: 2014-09-22 03:29:21.076836

"""

# revision identifiers, used by Alembic.
revision = '4015edc83ba'
down_revision = '4d10bc835f44'

from alembic import op
from sqlalchemy.sql import text


def upgrade():
    conn = op.get_bind()
    conn.execute(text('''
        ALTER TABLE calendar
            DROP FOREIGN KEY calendar_ibfk_1'''))
    conn.execute(text('''
        ALTER TABLE calendar
            CHANGE account_id namespace_id INTEGER NOT NULL'''))

    conn.execute(text('''
        ALTER TABLE calendar
            ADD FOREIGN KEY(namespace_id) REFERENCES namespace (id)
            '''))


def downgrade():
    raise Exception()
