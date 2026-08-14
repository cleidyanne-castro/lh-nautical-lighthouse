import pandas as pd
import psycopg2
from sklearn.metrics import mean_absolute_error


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "lh_nautical",
    "user": "annecastro"
}


PRODUCT_NAME = "Bússola de Bordo 702"


def get_sales_data():
    connection = psycopg2.connect(**DB_CONFIG)

    query = """
        SELECT
            o.placed_at,
            o.id AS order_id,
            oi.quantity,
            pv.id AS product_variant_id,
            p.id AS product_id,
            p.name AS product_name
        FROM orders o
        JOIN order_items oi
            ON oi.order_id = o.id
        JOIN product_variants pv
            ON pv.id = oi.product_variant_id
        JOIN products p
            ON p.id = pv.product_id
        WHERE p.name = %s
        ORDER BY o.placed_at;
    """

    df = pd.read_sql(
        query,
        connection,
        params=(PRODUCT_NAME,)
    )

    connection.close()

    return df


def create_monthly_sales(df):
    df["placed_at"] = pd.to_datetime(df["placed_at"])

    monthly = (
        df
        .set_index("placed_at")
        .resample("MS")["quantity"]
        .sum()
        .reset_index()
    )

    monthly.columns = ["month", "actual_sales"]

    return monthly


def create_forecast(monthly):
    monthly["forecast"] = (
        monthly["actual_sales"]
        .shift(1)
        .rolling(3)
        .mean()
    )

    return monthly


def evaluate_model(monthly):
    test = monthly[
        (monthly["month"] >= "2026-01-01")
        & (monthly["month"] <= "2026-03-01")
    ].copy()

    mae = mean_absolute_error(
        test["actual_sales"],
        test["forecast"]
    )

    return test, mae


def main():
    df = get_sales_data()

    print(f"Produto: {PRODUCT_NAME}")
    print(f"Registros encontrados: {len(df)}")
    print()

    monthly = create_monthly_sales(df)
    monthly = create_forecast(monthly)

    test, mae = evaluate_model(monthly)

    print("Previsão - Primeiro trimestre de 2026")
    print()

    print(
        test[
            ["month", "actual_sales", "forecast"]
        ].to_string(index=False)
    )

    print()
    print(f"MAE: {mae:.2f} unidades")


if __name__ == "__main__":
    main()