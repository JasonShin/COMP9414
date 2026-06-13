from __future__ import annotations

from typing import Any

from ai9414.search import run_graph_solver


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
    Return neighbouring nodes in deterministic DFS order.

    Important:
        The order matters. DFS follows the first unvisited neighbour it sees.
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
    stack: list[str],
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
        "stack": list(stack),
    }


def solve_dfs(graph: dict[str, Any]) -> dict[str, Any]:
    start = normalise_node_id(graph["start"])
    goal = normalise_node_id(graph["goal"])
    adjacency = build_adjacency(graph)

    # datastructures
    stack = [start]
    visited = { start }
    parents = {start: None}
    visited_order = [start]
    trace = []
    step = 0

    # Replace the placeholder result below with a full iterative DFS.
    trace.append(make_trace_event(step, "start", start, None, 0, stack))
    step += 1

    while stack:
        current = stack[-1]

        if current == goal:
            trace.append(make_trace_event(step, "found", current, parents[current], len(stack) - 1, stack))
            return {
                "algorithm": "dfs",
                "status": "found",
                "trace": trace,
                "path": reconstruct_path(parents, goal),
                "visited_order": visited_order,
            }

        neighbors = get_neighbours(adjacency, current)
        next_node = None
        for n in neighbors:
            if n not in visited:
                next_node = n
                break

        if next_node is not None:
            stack.append(next_node)
            visited.add(next_node)
            parents[next_node] = current
            visited_order.append(next_node)
            trace.append(make_trace_event(step, "expand", next_node, current, len(stack) - 1, stack))
            step += 1

        else:
            stack.pop()
            trace.append(make_trace_event(step, "backtrack", current, parents[current], len(stack) - 1, stack))
            step += 1


    return {
        "algorithm": "dfs",
        "status": "not_found",
        "message": "Replace the placeholder code inside solve_dfs with your full DFS implementation.",
        "trace": trace,
        "path": [],
        "visited_order": [start],
    }


if __name__ == "__main__":
    run_graph_solver(solve_dfs)
