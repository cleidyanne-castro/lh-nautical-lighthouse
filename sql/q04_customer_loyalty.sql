WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(total) AS faturamento_total,
        COUNT(id) AS frequencia,
        SUM(total) / COUNT(id) AS ticket_medio
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),

customer_categories AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
    JOIN order_items oi
        ON oi.order_id = o.id
    JOIN product_variants pv
        ON pv.id = oi.product_variant_id
    JOIN products p
        ON p.id = pv.product_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)

SELECT
    cs.customer_id,
    ROUND(cs.faturamento_total, 2) AS faturamento_total,
    cs.frequencia,
    ROUND(cs.ticket_medio, 2) AS ticket_medio,
    cc.diversidade_categorias
FROM customer_sales cs
JOIN customer_categories cc
    ON cc.customer_id = cs.customer_id
WHERE cc.diversidade_categorias >= 13
ORDER BY
    cs.ticket_medio DESC,
    cs.customer_id ASC
LIMIT 10;

WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(total) AS faturamento_total,
        COUNT(id) AS frequencia,
        SUM(total) / COUNT(id) AS ticket_medio
    FROM orders
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),

customer_categories AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
    JOIN order_items oi
        ON oi.order_id = o.id
    JOIN product_variants pv
        ON pv.id = oi.product_variant_id
    JOIN products p
        ON p.id = pv.product_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),

elite_customers AS (
    SELECT
        cs.customer_id,
        cs.ticket_medio
    FROM customer_sales cs
    JOIN customer_categories cc
        ON cc.customer_id = cs.customer_id
    WHERE cc.diversidade_categorias >= 13
    ORDER BY
        cs.ticket_medio DESC,
        cs.customer_id ASC
    LIMIT 10
)

SELECT
    p.category_id,
    c.name AS categoria,
    SUM(oi.quantity) AS total_itens
FROM elite_customers ec
JOIN orders o
    ON o.customer_id = ec.customer_id
JOIN order_items oi
    ON oi.order_id = o.id
JOIN product_variants pv
    ON pv.id = oi.product_variant_id
JOIN products p
    ON p.id = pv.product_id
JOIN categories c
    ON c.id = p.category_id
GROUP BY
    p.category_id,
    c.name
ORDER BY
    total_itens DESC,
    p.category_id ASC
LIMIT 1;


