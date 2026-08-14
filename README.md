# LH Nautical | Data & Analytics Engineering

Projeto desenvolvido como parte do desafio técnico da Indicium AI, com foco em Data Engineering, Analytics Engineering e geração de insights para negócio.

O objetivo foi transformar dados operacionais de uma empresa fictícia de varejo náutico em uma plataforma analítica confiável, organizada e pronta para apoiar decisões sobre vendas, clientes, estoque, devoluções e planejamento de demanda.

## Visão geral

A LH Nautical possui operações em lojas físicas e e-commerce, além de dados relacionados a clientes, pedidos, produtos, pagamentos, estoque, fornecedores, compras e devoluções.

A base original contém:

- 24 arquivos CSV relacionais
- Dados entre 2020 e 2026
- 48.998 pedidos
- 147.320 itens de pedidos
- 53.546 pagamentos
- 2.000 clientes
- 500 produtos
- 1.009 variantes de produtos

A solução foi construída de ponta a ponta, desde a estruturação dos dados até sua disponibilização em dashboards executivos e análises preditivas.

## Arquitetura da solução

```mermaid
flowchart LR
    A[24 CSVs] --> B[Python + SQL]
    B --> C[PostgreSQL]
    C --> D[DBeaver]
    A --> E[Databricks Bronze]
    E --> F[Databricks Silver]
    F --> G[Databricks Gold]
    G --> H[AI/BI Dashboard]
    G --> I[Forecast]
    G --> J[Recommendation]
