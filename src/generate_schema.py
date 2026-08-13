#!/usr/bin/env python3

import csv
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

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


def looks_like_numeric(value):
    try:
        Decimal(value)
        return True
    except (InvalidOperation, ValueError):
        return False


def looks_like_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def looks_like_timestamp(value):
    value = value.strip()

    # Formatos ISO comuns, inclusive com timezone.
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "T" in value or " " in value
    except ValueError:
        return False


def infer_column_type(column_name, values):
    """
    Infere um tipo PostgreSQL usando todos os valores não vazios da coluna.
    A inferência é conservadora: em caso de mistura de formatos, usa TEXT.
    """
    non_empty = [
        value.strip()
        for value in values
        if value is not None and value.strip() != ""
    ]

    if not non_empty:
        return "TEXT"

    normalized_name = column_name.lower()

    if any(hint in normalized_name for hint in TEXT_NAME_HINTS):
        return "TEXT"

    if all(looks_like_boolean(value) for value in non_empty):
        return "BOOLEAN"

    if all(looks_like_integer(value) for value in non_empty):
        return "BIGINT"

    if all(looks_like_numeric(value) for value in non_empty):
        return "NUMERIC"

    if all(looks_like_date(value) for value in non_empty):
        return "DATE"

    if all(looks_like_timestamp(value) for value in non_empty):
        return "TIMESTAMP"

    return "TEXT"


def inspect_csv(csv_path):
    """Lê um CSV e retorna suas colunas com os tipos PostgreSQL inferidos."""
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"CSV sem cabeçalho: {csv_path}")

        values_by_column = {
            column: []
            for column in reader.fieldnames
        }

        for row in reader:
            for column in reader.fieldnames:
                values_by_column[column].append(row.get(column, ""))

    return [
        (column, infer_column_type(column, values_by_column[column]))
        for column in reader.fieldnames
    ]


def build_create_table(table_name, columns):
    """Monta uma instrução CREATE TABLE para PostgreSQL."""
    column_definitions = [
        f"    {quote_identifier(column)} {data_type}"
        for column, data_type in columns
    ]

    return (
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)} (\n"
        + ",\n".join(column_definitions)
        + "\n);"
    )


def generate_schema(input_directory, output_file):
    """Processa todos os CSVs do diretório e gera um único schema.sql."""
    csv_files = sorted(
        file_name
        for file_name in os.listdir(input_directory)
        if file_name.lower().endswith(".csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum arquivo CSV encontrado em: {input_directory}"
        )

    statements = [
        "-- Schema gerado automaticamente a partir dos CSVs da LH Nautical",
        "-- Banco de destino: PostgreSQL",
        f"-- Total de tabelas: {len(csv_files)}",
        "",
    ]

    for file_name in csv_files:
        csv_path = os.path.join(input_directory, file_name)
        table_name = os.path.splitext(file_name)[0]

        columns = inspect_csv(csv_path)
        statements.append(build_create_table(table_name, columns))
        statements.append("")

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(statements))

    print(f"Schema gerado com sucesso: {output_file}")
    print(f"Tabelas processadas: {len(csv_files)}")


if __name__ == "__main__":
    INPUT_DIRECTORY = "lh_nautical_csv"
    OUTPUT_FILE = "schema.sql"

    generate_schema(INPUT_DIRECTORY, OUTPUT_FILE)
