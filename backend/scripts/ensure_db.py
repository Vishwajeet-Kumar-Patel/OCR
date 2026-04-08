import psycopg

CONN_STR = "host=127.0.0.1 port=5432 user=postgres password=Vish@1011 dbname=postgres"
TARGET_DB = "ad_prompt_ai"


def main() -> None:
    with psycopg.connect(CONN_STR) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TARGET_DB,))
            exists = cur.fetchone() is not None
            print(f"exists_before={exists}")
            if not exists:
                cur.execute(f"CREATE DATABASE {TARGET_DB}")
                print("created")
            else:
                print("already_exists")


if __name__ == "__main__":
    main()
