import pandas as pd
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "lh_nautical",
    "user": "annecastro"
}

REFERENCE_PRODUCT = "Motor de Popa 1949"


def load_data():
    connection = psycopg2.connect(**DB_CONFIG)

    query = """
        SELECT
            o.customer_id,
            p.id AS product_id,
            p.name AS product_name
        FROM orders o
        JOIN order_items oi
            ON oi.order_id = o.id
        JOIN product_variants pv
            ON pv.id = oi.product_variant_id
        JOIN products p
            ON p.id = pv.product_id
        WHERE o.customer_id IS NOT NULL;
    """

    df = pd.read_sql(query, connection)
    connection.close()

    return df


def build_interaction_matrix(df):
    interaction = (
        df.assign(purchased=1)
        .drop_duplicates(["customer_id", "product_id"])
        .pivot(
            index="customer_id",
            columns="product_id",
            values="purchased"
        )
        .fillna(0)
    )

    return interaction


def get_recommendations(df, interaction):
    product_names = (
        df[["product_id", "product_name"]]
        .drop_duplicates()
        .set_index("product_id")["product_name"]
    )

    reference_ids = product_names[
        product_names == REFERENCE_PRODUCT
    ].index

    if len(reference_ids) == 0:
        raise ValueError("Produto de referência não encontrado.")

    reference_id = reference_ids[0]

    product_matrix = interaction.T

    similarities = cosine_similarity(product_matrix)

    similarity_df = pd.DataFrame(
        similarities,
        index=product_matrix.index,
        columns=product_matrix.index
    )

    ranking = (
        similarity_df[reference_id]
        .drop(reference_id)
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    ranking.columns = ["product_id", "similarity"]

    ranking["product_name"] = ranking["product_id"].map(product_names)

    return ranking[
        ["product_id", "product_name", "similarity"]
    ]


def main():
    df = load_data()

    interaction = build_interaction_matrix(df)

    ranking = get_recommendations(
        df,
        interaction
    )

    print(f"Produto de referência: {REFERENCE_PRODUCT}")
    print()
    print("Top 5 produtos mais similares:")
    print()
    print(ranking.to_string(index=False))


if __name__ == "__main__":
    main()