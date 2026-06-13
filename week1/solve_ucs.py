from __future__ import annotations

import heapq
from typing import Any

from ai9414.search import run_graph_ucs_solver


def normalise_node_id(raw: Any) -> str:
    """
    Convert one node id into a Python string.
    """
    return str(raw)


def build_adjacency(graph: dict[str, Any]) -> dict[str, list[tuple[str, float]]]:
    """
    Build an adjacency list from the weighted graph dictionary.

    The graph uses this format:
        {
            "nodes": [{"id": "A", "x": 0.1, "y": 0.2}, ...],
            "edges": [{"u": "A", "v": "B", "cost": 1.7}, ...],
            "start": "A",
            "goal": "G"
        }
    """
    adjacency = {str(node["id"]): [] for node in graph["nodes"]}
    for edge in graph["edges"]:
        left = str(edge["u"])
        right = str(edge["v"])
        cost = float(edge["cost"])
        adjacency[left].append((right, cost))
        adjacency[right].append((left, cost))
    for node_id in adjacency:
        adjacency[node_id].sort(key=lambda item: (item[1], item[0]))
    return adjacency


def get_neighbours(adjacency: dict[str, list[tuple[str, float]]], node_id: str) -> list[tuple[str, float]]:
    """
    Return neighbouring nodes in deterministic UCS order.

    Important:
        The order matters. The demo expects a fixed order for a fixed graph.
    """
    return list(adjacency[node_id])


def reconstruct_path(parents: dict[str, str | None], goal: str) -> list[str]:
    """
    Reconstruct the final path from the start node to the goal node.
    """
    path: list[str] = []
    current: str | None = goal
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return path


def make_trace_event(
    step: int,
    action: str,
    node_id: str | None,
    parent: str | None,
    depth: int,
    path_cost: float,
    current_path: list[str],
    current_cost: float,
    best_path: list[str],
    best_cost: float | None,
    considered_edge: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build one trace event for the replay.

    The browser uses this event format directly.
    """
    return {
        "step": step,
        "action": action,
        "node": node_id,
        "parent": parent,
        "depth": depth,
        "path_cost": float(path_cost),
        "current_path": list(current_path),
        "current_cost": float(current_cost),
        "best_path": list(best_path),
        "best_cost": None if best_cost is None else float(best_cost),
        "considered_edge": None if considered_edge is None else list(considered_edge),
    }


def solve_ucs(graph: dict[str, Any]) -> dict[str, Any]:
    start = normalise_node_id(graph["start"])
    goal = normalise_node_id(graph["goal"])
    adjacency = build_adjacency(graph)

    frontier = [(0, start)]
    parents: dict[str, str | None] = {start: None}
    visited = set()
    best_costs: dict[str, float] = {start: 0.0}
    visited_order: list[str] = []
    steps = 0

    heapq.heapify(frontier)

    trace = [make_trace_event(0, "start", start, None, 0, 0.0, [start], 0.0, [], None)]

    steps += 1

    while frontier:
        cost, node = heapq.heappop(frontier)

        if node in visited:
            continue

        visited.add(node)
        visited_order.append(node)

        if node == goal:
            trace.append(make_trace_event(steps, "found", node, parents[node], len(frontier), cost, [node], cost, [node], cost))
            return {
                "algorithm": "ucs",
                "status": "found",
                "trace": trace,
                "path": reconstruct_path(parents, goal),
                "best_cost": cost,
                "visited_order": visited_order,
            }

        for neighbor, edge_cost in get_neighbours(adjacency, node):
            new_cost = cost + edge_cost
            if neighbor not in best_costs or new_cost < best_costs[neighbor]:
                best_costs[neighbor] = new_cost
                parents[neighbor] = node
                heapq.heappush(frontier, (new_cost, neighbor))
                trace.append(make_trace_event(steps, "expand", neighbor, node, len(frontier), new_cost, [neighbor], new_cost, reconstruct_path(parents, neighbor), new_cost, [node, neighbor]))
                steps += 1

    trace.append(make_trace_event(steps, "fail", None, None, 0, 0.0, [], 0.0, [], None))
    return {
        "algorithm": "ucs",
        "status": "not_found",
        "message": "Replace the placeholder code inside solve_ucs with your full UCS implementation.",
        "trace": trace,
        "path": [],
        "best_cost": None,
        "visited_order": visited_order,
    }


if __name__ == "__main__":
    run_graph_ucs_solver(solve_ucs)
