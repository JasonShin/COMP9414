from __future__ import annotations

import heapq
import math
from typing import Any

from ai9414.search import run_graph_astar_solver


def normalise_node_id(raw: Any) -> str:
    """
    Convert one node id into a Python string.
    """
    return str(raw)


def build_adjacency(graph: dict[str, Any]) -> dict[str, list[tuple[str, float]]]:
    """
    Build an adjacency list from the weighted graph dictionary.
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


def heuristic_to_goal(graph: dict[str, Any], node_id: str) -> float:
    """
    Return the straight-line distance from node_id to the goal node.
    """
    positions = {str(node["id"]): (float(node["x"]), float(node["y"])) for node in graph["nodes"]}
    goal = normalise_node_id(graph["goal"])
    return math.dist(positions[node_id], positions[goal])


def get_neighbours(adjacency: dict[str, list[tuple[str, float]]], node_id: str) -> list[tuple[str, float]]:
    """
    Return neighbouring nodes in deterministic order.
    """
    return list(adjacency[node_id])


def make_trace_event(
    step: int,
    action: str,
    node_id: str | None,
    parent: str | None,
    depth: int,
    path_cost: float,
    current_path: list[str],
    current_cost: float,
    heuristic: float,
    priority: float,
    best_cost: float | None,
    considered_edge: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build one trace event for the replay.
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
        "heuristic": float(heuristic),
        "priority": float(priority),
        "best_cost": None if best_cost is None else float(best_cost),
        "considered_edge": None if considered_edge is None else list(considered_edge),
    }


def solve_astar(graph: dict[str, Any]) -> dict[str, Any]:
    """
    Solve the weighted graph with A* search.

    This is the main function you are expected to implement.
    You should replace the TODO section below with a complete A* solver.

    Student responsibilities:
        - build or use an adjacency structure
        - compute the heuristic distance from each node to the goal
        - keep the best known path cost g(n) to each node
        - order the priority queue by f(n) = g(n) + h(n)
        - record visited_order
        - return the final optimal path and best cost
        - build the trace list

    Important:
        The heuristic here is straight-line distance to the goal.
        Because the edge costs are also geometric distances, this heuristic is admissible.
    """
    start = normalise_node_id(graph["start"])
    goal = normalise_node_id(graph["goal"])
    adjacency = build_adjacency(graph)

    h_start = heuristic_to_goal(graph, "start")
    frontier = [(h_start, 0.0, 0, start, [start])]
    best_costs = {start: 0.0}
    visited = set()
    visited_order = []
    counter = 1
    trace = []

    def add_step(action, node, parent, depth, path, cost, edge=None):
        heuristic = heuristic_to_goal(graph, node) if node is not None else 0.0
        trace.append({
            "step": len(trace),
            "action": action,
            "node": node,
            "parent": parent,
            "depth": depth,
            "path_cost": float(cost),
            "current_path": list(path),
            "current_cost": float(cost),
            "heuristic": float(heuristic),
            "priority": float(cost + heuristic),
            "best_cost": float(cost) if path else None,
            "considered_edge": edge,
        })

    while frontier:
        _, cost, _, node, path = heapq.heappop(frontier)
        if cost != best_costs.get(node):
            continue

        depth = len(path) - 1
        add_step("expanded", node, path[-2] if depth else None, depth, path, cost)
        if node == goal:
            return {
                "algorithm": "astar",
                "status": "found",
                "trace": trace,
                "path": path,
                "best_cost": cost,
                "visited_order": visited_order,
            }

        visited.add(node)
        for neighbour, edge_cost in get_neighbours(adjacency, node):
            new_cost = cost + edge_cost
            new_path = path + [neighbour]
            add_step("consider_edge", node, path[-2] if depth else None, depth, path, cost, [node, neighbour])
            too_expensive = new_cost >= best_costs.get(neighbour, float("inf"))

            if neighbour in visited and too_expensive:
                continue

            if new_cost < best_costs.get(neighbour, float("inf")):
                best_costs[neighbour] = new_cost
                if neighbour not in visited:
                    visited.add(neighbour)
                    visited_order.append(neighbour)
                add_step("relax", neighbour, node, depth + 1, new_path, new_cost)
                priority = new_cost + heuristic_to_goal(adjacency, neighbour)
                heapq.heappush(frontier, (priority, new_cost, counter, neighbour, new_path))
                counter += 1

    trace.append(
        {
            "step": len(trace),
            "action": "fail",
            "node": None,
            "parent": None,
            "depth": 0,
            "path_cost": 0.0,
            "current_path": [],
            "current_cost": 0.0,
            "heuristic": 0.0,
            "priority": 0.0,
            "best_cost": None,
            "considered_edge": None,
        }
    )
    return {
        "algorithm": "astar",
        "status": "not_founded",
        "trace": trace,
        "path": [],
        "best_cost": None,
        "visited_order": visited_order,
    }


if __name__ == "__main__":
    run_graph_astar_solver(solve_astar)
