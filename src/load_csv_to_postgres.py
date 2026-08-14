import csv
import os
import psycopg2
from psycopg2 import sql


CSV_FOLDER = "/Users/annecastro/lh-nautical-lighthouse-local/lh_nautical_csv"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "lh_nautical",
    "user": "annecastro"
}


def load_csv(connection, file_path, table_name):
    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        columns = next(reader)

    column_list = sql.SQL(", ").join(
        sql.Identifier(column)
        for column in columns
    )

    copy_command = sql.SQL(
        """
        COPY {} ({})
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE,
            ENCODING 'UTF8'
        )
        """
    ).format(
        sql.Identifier(table_name),
        column_list
    )

    with connection.cursor() as cursor:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            cursor.copy_expert(
                copy_command.as_string(connection),
                file
            )


def load_all_csvs():
    connection = psycopg2.connect(**DB_CONFIG)

    files = sorted(
        file_name
        for file_name in os.listdir(CSV_FOLDER)
        if file_name.endswith(".csv")
    )

    try:
        for file_name in files:
            file_path = os.path.join(
                CSV_FOLDER,
                file_name
            )

            table_name = os.path.splitext(file_name)[0]

            load_csv(
                connection,
                file_path,
                table_name
            )

            connection.commit()

            print(f"{table_name}: carregado com sucesso")

        print()
        print(f"Arquivos processados: {len(files)}")

    except Exception as error:
        connection.rollback()
        print(f"Erro durante o carregamento: {error}")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_all_csvs()