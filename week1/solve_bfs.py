from __future__ import annotations

from collections import deque
from typing import Any

from ai9414.search import run_graph_bfs_solver


def normalise_node_id(raw: Any) -> str:
    """
    Convert one node id into a Python string.

    Example:
        normalise_node_id("A") returns "A".
    """
    return str(raw)


def build_adjacency(graph: dict[str, Any]) -> dict[str, list[str]]:
    """
    Build an adjacency list from the graph dictionary.

    The graph uses this format:
        {
            "nodes": [{"id": "A", "x": 0.1, "y": 0.2}, ...],
            "edges": [{"u": "A", "v": "B"}, ...],
            "start": "A",
            "goal": "G"
        }
    """
    adjacency = {str(node["id"]): [] for node in graph["nodes"]}
    for edge in graph["edges"]:
        left = str(edge["u"])
        right = str(edge["v"])
        adjacency[left].append(right)
        adjacency[right].append(left)
    for node_id in adjacency:
        adjacency[node_id].sort()
    return adjacency


def get_neighbours(adjacency: dict[str, list[str]], node_id: str) -> list[str]:
    """
    Return neighbouring nodes in deterministic BFS order.

    Important:
        The order matters. BFS visits each layer in this neighbour order.
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
    route: list[str],
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
        "route": list(route),
    }


def solve_bfs(graph: dict[str, Any]) -> dict[str, Any]:
    # Iterative Breadth-First Search (BFS) using a queue (FIFO).
    #
    # How it works visually:
    #
    #   BFS explores the graph LAYER BY LAYER, like ripples spreading from a stone.
    #   Unlike DFS (which dives deep), BFS visits ALL nodes at depth d before depth d+1.
    #   This guarantees the SHORTEST path (by number of edges).
    #
    #   Example with start=S, neighbours sorted alphabetically:
    #
    #   Step 0 (start):     queue = [S]           depth 0
    #                       Pop S. Expand its neighbours H, M, N.
    #
    #   Step 1 (expand H):  queue = [M, N, H]  →  queue = [M, N, H]
    #   Step 2 (expand M):  queue = [N, H, M]     depth 1 — all of S's neighbours
    #   Step 3 (expand N):  queue = [H, M, N]
    #
    #   Now pop H (front of queue). Expand H's unvisited neighbours...
    #   Step 4 (expand E):  queue = [M, N, E]     depth 2 — neighbours of H
    #   Step 5 (expand K):  queue = [N, E, K]
    #
    #   Pop M. Expand M's unvisited neighbours...
    #   Step 6 (expand A):  queue = [E, K, A]     depth 2 — neighbours of M
    #
    #   ... continues layer by layer until goal is found or queue is empty.
    #
    #   Key idea: BFS never backtracks. It just drains the queue level by level.
    #   The queue always holds the frontier — nodes discovered but not yet processed.

    start = normalise_node_id(graph["start"])
    goal = normalise_node_id(graph["goal"])
    adjacency = build_adjacency(graph)

    # Data structures
    queue = deque([start])       # FIFO frontier — pop from left, push to right
    visited = {start}            # nodes we've already seen (never revisit)
    parents = {start: None}      # parent pointers for path reconstruction
    depths = {start: 0}          # track each node's depth for the trace
    visited_order = [start]      # discovery order for the trace
    trace = []
    step = 0

    # Emit the initial "start" event — we're at the start node, depth 0
    trace.append(make_trace_event(step, "start", start, None, 0, [start]))
    step += 1

    while queue:
        node = queue.popleft()   # take the OLDEST node (FIFO = breadth-first)

        # Goal check: if the node we just dequeued is the goal, we're done
        if node == goal:
            path = reconstruct_path(parents, goal)
            trace.append(make_trace_event(step, "found", node, parents[node], depths[node], path))
            return {
                "algorithm": "bfs",
                "status": "found",
                "trace": trace,
                "path": path,
                "visited_order": visited_order,
            }

        # Expand: enqueue ALL unvisited neighbours (sorted for determinism)
        neighbors = get_neighbours(adjacency, node)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parents[neighbor] = node
                depths[neighbor] = depths[node] + 1
                queue.append(neighbor)
                visited_order.append(neighbor)
                route = reconstruct_path(parents, neighbor)
                trace.append(make_trace_event(step, "expand", neighbor, node, depths[neighbor], route))
                step += 1

    # Queue is empty — we explored everything reachable and never found the goal
    trace.append(make_trace_event(step, "fail", None, None, 0, []))
    return {
        "algorithm": "bfs",
        "status": "not_found",
        "trace": trace,
        "path": [],
        "visited_order": visited_order,
    }


if __name__ == "__main__":
    run_graph_bfs_solver(solve_bfs)
