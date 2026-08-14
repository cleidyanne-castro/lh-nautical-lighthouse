#!/usr/bin/env python3

import csv
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation


def is_boolean(value):
    return value.lower() in {"true", "false"}


def is_integer(value):
TEXT_NAME_HINTS = (
    "name",
    "number",
    "sku",
    "barcode",
    "tax_id",
    "cpf",
    "cnpj",
    "phone",
    "postal_code",
    "ncm",
    "series",
    "access_key",
    "email",
    "uri",
    "slug",
    "country",
    "state",
    "currency",
)


def quote_identifier(name):
    """Escapa nomes de tabelas/colunas para uso seguro no PostgreSQL."""
    return '"' + name.replace('"', '""') + '"'


def looks_like_boolean(value):
    return value.strip().lower() in {"true", "false"}


def looks_like_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_numeric(value):
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False


def is_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_timestamp(value):
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "T" in value or " " in value
    except ValueError:
        return False


def infer_type(values):
    values = [v.strip() for v in values if v and v.strip()]

    if not values:
        return "TEXT"

    if all(is_boolean(v) for v in values):
        return "BOOLEAN"

    if all(is_integer(v) for v in values):
        return "BIGINT"

    if all(is_numeric(v) for v in values):
        return "NUMERIC"

    if all(is_date(v) for v in values):
        return "DATE"

    if all(is_timestamp(v) for v in values):
        return "TIMESTAMP"

    return "TEXT"


def read_csv_schema(file_path):
    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        columns = {
            name: []
            for name in reader.fieldnames
        }

        for row in reader:
            for column in reader.fieldnames:
                columns[column].append(row[column])

    return {
        column: infer_type(values)
        for column, values in columns.items()
    }


def create_table_sql(table_name, schema):
    columns = []

    for column_name, column_type in schema.items():
        columns.append(
            f'    "{column_name}" {column_type}'
        )

    return (
        f'CREATE TABLE "{table_name}" (\n'
        + ",\n".join(columns)
        + "\n);"
    )


def generate_schema(input_folder, output_file):
    sql_commands = []

    files = sorted(os.listdir(input_folder))

    for file_name in files:
        if not file_name.endswith(".csv"):
            continue

        file_path = os.path.join(
            input_folder,
            file_name
        )

        table_name = os.path.splitext(file_name)[0]

        schema = read_csv_schema(file_path)

        sql_commands.append(
            create_table_sql(
                table_name,
                schema
            )
        )

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n\n".join(sql_commands))

    print(f"{len(sql_commands)} tabelas processadas.")
    print(f"Arquivo criado: {output_file}")


if __name__ == "__main__":
    input_folder = "/Users/annecastro/lh-nautical-lighthouse-local/lh_nautical_csv"
    output_file = "/Users/annecastro/lh-nautical-lighthouse/sql/schema.sql"

    generate_schema(
        input_folder,
        output_file
    )