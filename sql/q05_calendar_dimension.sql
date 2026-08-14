WITH limites AS (
    SELECT
        MIN(placed_at::date) AS data_inicial,
        MAX(placed_at::date) AS data_final
    FROM orders
),

calendario AS (
    SELECT
        data::date AS data,
        EXTRACT(ISODOW FROM data) AS numero_dia_semana,
        CASE EXTRACT(ISODOW FROM data)
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
            WHEN 7 THEN 'Domingo'
        END AS dia_semana
    FROM limites,
    generate_series(
        data_inicial,
        data_final,
        interval '1 day'
    ) AS data
),

vendas_diarias AS (
    SELECT
        placed_at::date AS data,
        SUM(total) AS total_vendas
    FROM orders
    WHERE channel = 'pos'
    GROUP BY placed_at::date
),

calendario_com_vendas AS (
    SELECT
        c.data,
        c.numero_dia_semana,
        c.dia_semana,
        COALESCE(v.total_vendas, 0) AS total_vendas
    FROM calendario c
    LEFT JOIN vendas_diarias v
        ON v.data = c.data
)

SELECT
    dia_semana,
    ROUND(AVG(total_vendas), 2) AS media_vendas
FROM calendario_com_vendas
GROUP BY
    numero_dia_semana,
    dia_semana
ORDER BY media_vendas ASC;