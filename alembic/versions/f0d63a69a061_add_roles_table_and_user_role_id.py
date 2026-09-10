"""add roles table and user role_id

Revision ID: f0d63a69a061
Revises: afb851d7f794
Create Date: 2026-09-10 15:40:30.942150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from utilities.roles import DEFAULT_ROLES

# revision identifiers, used by Alembic.
revision: str = 'f0d63a69a061'
down_revision: Union[str, Sequence[str], None] = 'afb851d7f794'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NAME = 'fk_users_role_id_roles'
DEFAULT_USER_ROLE = DEFAULT_ROLES[-1][0]  # "user" — assigned to any pre-existing rows


def upgrade() -> None:
    """Upgrade schema."""
    roles_table = op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_role'), 'roles', ['role'], unique=True)

    op.bulk_insert(
        roles_table,
        [{'role': role, 'description': description} for role, description in DEFAULT_ROLES],
    )

    # Add as nullable first so any pre-existing rows can be backfilled,
    # then tighten to NOT NULL once every row has a role.
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(FK_NAME, 'users', 'roles', ['role_id'], ['id'])

    users_table = sa.table('users', sa.column('role_id', sa.Integer))
    default_role_id = sa.select(roles_table.c.id).where(roles_table.c.role == DEFAULT_USER_ROLE).scalar_subquery()
    op.execute(users_table.update().values(role_id=default_role_id))

    op.alter_column('users', 'role_id', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(FK_NAME, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    op.drop_index(op.f('ix_roles_role'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
