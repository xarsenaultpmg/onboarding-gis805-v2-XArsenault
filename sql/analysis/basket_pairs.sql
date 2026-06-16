-- S04 — Analyse de panier : paires de produits co-achetés (self-join sur fact_sales).
-- Grain panier : order_number (dimension dégénérée). Pas de doublons (A,B) vs (B,A).

-- Top 20 paires par fréquence (noms + catégories)
SELECT
    pa.name AS product_a_name,
    pa.category AS product_a_category,
    pb.name AS product_b_name,
    pb.category AS product_b_category,
    COUNT(*) AS times_bought_together
FROM fact_sales AS f1
INNER JOIN fact_sales AS f2
    ON  f1.order_number = f2.order_number
    AND f1.product_key < f2.product_key
INNER JOIN dim_product AS pa ON f1.product_key = pa.product_key
INNER JOIN dim_product AS pb ON f2.product_key = pb.product_key
GROUP BY pa.name, pa.category, pb.name, pb.category
ORDER BY times_bought_together DESC
LIMIT 20;

-- Stretch : paires cross-catégorie (opportunités de vente croisée)
SELECT
    pa.category AS category_a,
    pb.category AS category_b,
    COUNT(*) AS cross_category_pairs
FROM fact_sales AS f1
INNER JOIN fact_sales AS f2
    ON  f1.order_number = f2.order_number
    AND f1.product_key < f2.product_key
INNER JOIN dim_product AS pa ON f1.product_key = pa.product_key
INNER JOIN dim_product AS pb ON f2.product_key = pb.product_key
WHERE pa.category < pb.category
GROUP BY pa.category, pb.category
ORDER BY cross_category_pairs DESC
LIMIT 10;
