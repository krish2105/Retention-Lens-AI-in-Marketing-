"""Co-purchase network (week 9): products bought on the same invoice, with communities."""
from __future__ import annotations

from collections import Counter
from itertools import combinations

import networkx as nx
import pandas as pd


def co_purchase_graph(lines: pd.DataFrame, top_products: int = 120, min_pairs: int = 60) -> nx.Graph:
    sales = lines[lines["is_sale"]][["invoice", "stock_code", "description"]].drop_duplicates(["invoice", "stock_code"])
    counts = sales["stock_code"].value_counts()
    keep = set(counts.head(top_products).index)
    sales = sales[sales["stock_code"].isin(keep)]
    names = sales.drop_duplicates("stock_code").set_index("stock_code")["description"].fillna("").to_dict()
    invoices = sales["invoice"].nunique()
    pairs: Counter = Counter()
    for items in sales.groupby("invoice")["stock_code"].apply(sorted):
        pairs.update(combinations(items, 2))
    graph = nx.Graph()
    for code in keep:
        graph.add_node(code, label=str(names.get(code, code)).title(), invoices=int(counts[code]))
    for (a, b), n in pairs.items():
        if n >= min_pairs:
            lift = n * invoices / (counts[a] * counts[b])
            graph.add_edge(a, b, weight=int(n), lift=round(float(lift), 2))
    graph.remove_nodes_from([n for n in list(graph.nodes) if graph.degree(n) == 0])
    return graph


def network_payload(graph: nx.Graph, seed: int = 42) -> dict:
    communities = nx.community.greedy_modularity_communities(graph, weight="weight")
    community_of = {node: i for i, members in enumerate(communities) for node in members}
    layout = nx.spring_layout(graph, weight="weight", seed=seed, k=0.35)
    centrality = nx.degree_centrality(graph)
    nodes = [
        {"id": n, "label": d["label"], "invoices": d["invoices"], "community": community_of[n],
         "degree": graph.degree(n), "centrality": round(centrality[n], 4), "x": round(float(layout[n][0]), 4), "y": round(float(layout[n][1]), 4)}
        for n, d in graph.nodes(data=True)
    ]
    edges = sorted(({"a": a, "b": b, **d} for a, b, d in graph.edges(data=True)), key=lambda e: -e["weight"])
    return {
        "nodes": nodes,
        "edges": edges[:400],
        "communities": [
            {"id": i, "size": len(m), "examples": [graph.nodes[n]["label"] for n in sorted(m, key=lambda n: -graph.nodes[n]["invoices"])[:4]]}
            for i, m in enumerate(communities)
        ],
        "modularity": round(float(nx.community.modularity(graph, communities, weight="weight")), 4),
        "method": "Top products by invoice count; edge when bought together on ≥ the minimum number of invoices; greedy modularity communities",
    }
