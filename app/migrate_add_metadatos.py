# migrate_add_metadatos.py
import os
import sys
import argparse
import psycopg2

SQL = """
BEGIN;

-- Asegura la extension para indices GIN en jsonb (normalmente ya disponible)
-- (No requiere CREATE EXTENSION para GIN; viene por defecto)

ALTER TABLE productos
  ADD COLUMN IF NOT EXISTS metadatos jsonb NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_productos_metadatos_gin
  ON productos USING GIN (metadatos);

COMMIT;
"""

def main():
    parser = argparse.ArgumentParser(description="Add columna jsonb 'metadatos' a productos (idempotente).")
    parser.add_argument("--dsn", help="Cadena DSN de PostgreSQL. Ej: postgresql://user:pass@host:puerto/db", required=True)
    args = parser.parse_args()
    try:
        conn = psycopg2.connect(args.dsn)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(SQL)
        conn.commit()
        print("Migracion aplicada correctamente.")
    except Exception as e:
        print(f"Error durante la migracion: {e}", file=sys.stderr)
        try:
            conn.rollback()
        except Exception:
            pass
        sys.exit(1)
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()

