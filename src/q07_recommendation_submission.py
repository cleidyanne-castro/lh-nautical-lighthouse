import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


DATA_FOLDER = "/Users/annecastro/lh-nautical-lighthouse-local/lh_nautical_csv"

REFERENCE_PRODUCT = "Motor de Popa 1949"


def load_data():
    orders = pd.read_csv(f"{DATA_FOLDER}/orders.csv")
    order_items = pd.read_csv(f"{DATA_FOLDER}/order_items.csv")
    product_variants = pd.read_csv(f"{DATA_FOLDER}/product_variants.csv")
    products = pd.read_csv(f"{DATA_FOLDER}/products.csv")

    df = (
        orders[["id", "customer_id"]]
        .merge(
            order_items[["order_id", "product_variant_id"]],
            left_on="id",
            right_on="order_id"
        )
        .merge(
            product_variants[["id", "product_id"]],
            left_on="product_variant_id",
            right_on="id"
        )
        .merge(
            products[["id", "name"]],
            left_on="product_id",
            right_on="id"
        )
    )

    df = df[
        ["customer_id", "product_id", "name"]
    ].rename(
        columns={"name": "product_name"}
    )

    return df


def build_interaction_matrix(df):
    df = df.dropna(subset=["customer_id"])

    df = df.drop_duplicates(
        ["customer_id", "product_id"]
    )

    df["purchased"] = 1

    matrix = df.pivot(
        index="customer_id",
        columns="product_id",
        values="purchased"
    ).fillna(0)

    return matrix


def build_similarity_ranking(df, interaction_matrix):
    product_names = (
        df[["product_id", "product_name"]]
        .drop_duplicates()
        .set_index("product_id")["product_name"]
    )

    reference_id = product_names[
        product_names == REFERENCE_PRODUCT
    ].index[0]

    product_matrix = interaction_matrix.T

    similarity_matrix = cosine_similarity(
        product_matrix
    )

    similarity_df = pd.DataFrame(
        similarity_matrix,
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

    ranking.columns = [
        "product_id",
        "similarity"
    ]

    ranking["product_name"] = (
        ranking["product_id"]
        .map(product_names)
    )

    return ranking[
        ["product_id", "product_name", "similarity"]
    ]


def main():
    df = load_data()

    interaction_matrix = build_interaction_matrix(df)

    ranking = build_similarity_ranking(
        df,
        interaction_matrix
    )

    print(
        f"Produto de referência: {REFERENCE_PRODUCT}"
    )

    print()

    print("Top 5 produtos mais similares:")

    print()

    print(
        ranking.to_string(index=False)
    )


if __name__ == "__main__":
    main()