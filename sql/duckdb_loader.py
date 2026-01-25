import duckdb
import sys
import os

DB_PATH = "data/project.db"

def load_csv(csv_path, table_name):
    if not os.path.exists(csv_path):
        print(f" Fichier introuvable : {csv_path}")
        return

    con = duckdb.connect(DB_PATH)

    print(f"\n Chargement de {csv_path} dans la table '{table_name}' ...")

    con.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM read_csv_auto('{csv_path}')
    """)

    rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f" {rows} lignes chargées dans '{table_name}'")

    print(f"\n Colonnes de la table '{table_name}' :")
    print(con.execute(f"DESCRIBE {table_name}").fetchdf())

    con.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    csv_file = sys.argv[1]
    table = sys.argv[2]

    load_csv(csv_file, table)
