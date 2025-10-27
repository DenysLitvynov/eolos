"""Actualizar mibisivalencia a solo targeta_id como String

Revision ID: 00ddd39d1525
Revises: 
Create Date: 2025-10-27 20:21:40.250261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00ddd39d1525'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from sqlalchemy.dialects import postgresql

def upgrade():
    # 1. Dropear la constraint de FK para evitar el mismatch
    op.drop_constraint('usuarios_targeta_id_fkey', 'usuarios', type_='foreignkey')

    # 2. Alterar la columna primaria en mibisivalencia (referenciada)
    op.alter_column(
        'mibisivalencia',
        'targeta_id',
        existing_type=sa.UUID(),
        type_=sa.String(length=9),
        existing_nullable=False,
        postgresql_using='targeta_id::varchar(9)'  # Intenta convertir; fallará si datos no caben en 9 chars
    )

    # 3. Alterar la columna FK en usuarios
    op.alter_column(
        'usuarios',
        'targeta_id',
        existing_type=sa.UUID(),
        type_=sa.String(length=9),
        existing_nullable=True,
        postgresql_using='targeta_id::varchar(9)'  # Igual, conversión tentativa
    )

    # 4. Alterar usuario_id (no afecta FK, pero inclúyelo)
    op.alter_column(
        'usuarios',
        'usuario_id',
        existing_type=sa.UUID(),
        type_=sa.String(length=36),
        existing_nullable=False,
        postgresql_using='usuario_id::varchar(36)'  # UUID cabe en 36 chars
    )

    # 5. Recrear la FK con los tipos nuevos
    op.create_foreign_key(
        'usuarios_targeta_id_fkey',  # Nombre de la constraint (debe coincidir con el original)
        'usuarios',                  # Tabla que referencia
        'mibisivalencia',            # Tabla referenciada
        ['targeta_id'],              # Columna local
        ['targeta_id'],              # Columna remota
        ondelete='SET NULL'          # Mantén el comportamiento original de tu models.py
    )

def downgrade():
    # Invierte los pasos para downgrade (dropea FK, altera tipos de vuelta, recrea FK)
    op.drop_constraint('usuarios_targeta_id_fkey', 'usuarios', type_='foreignkey')
    op.alter_column('usuarios', 'usuario_id', existing_type=sa.String(length=36), type_=sa.UUID(), existing_nullable=False, postgresql_using='usuario_id::uuid')
    op.alter_column('usuarios', 'targeta_id', existing_type=sa.String(length=9), type_=sa.UUID(), existing_nullable=True, postgresql_using='targeta_id::uuid')
    op.alter_column('mibisivalencia', 'targeta_id', existing_type=sa.String(length=9), type_=sa.UUID(), existing_nullable=False, postgresql_using='targeta_id::uuid')
    op.create_foreign_key('usuarios_targeta_id_fkey', 'usuarios', 'mibisivalencia', ['targeta_id'], ['targeta_id'], ondelete='SET NULL')
