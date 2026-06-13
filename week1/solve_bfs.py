from __future__ import annotations

from collections import deque
from queue import PriorityQueue
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
    """
    Solve the graph using breadth-first search and return a full result.

    This is the main function you are expected to implement.
    You should replace the TODO section below with a complete iterative BFS.

    Student responsibilities:
        - build or use an adjacency structure
        - run BFS
        - record visited_order
        - reconstruct the final path
        - build the trace list

    ai9414 responsibilities:
        - start the local web server
        - expose the /solve endpoint
        - pass the graph dictionary into this function
        - validate the result shape
        - send the result back to the browser

    Required return format:
        {
            "algorithm": "bfs",
            "status": "found" or "not_found",
            "trace": [...],
            "path": ["A", "B", "G"],
            "visited_order": ["A", "B", "D", "G"],
        }

    Trace actions:
        - start: emit once at the start node
        - expand: emit when BFS discovers a new node
        - found: emit once when the goal is reached
        - fail: emit once if the frontier empties and no goal path exists

    Suggested plan:
        1. Parse the start and goal ids.
        2. Build the adjacency list.
        3. Initialise a queue, visited set, parents, trace, visited_order, and step.
        4. Emit the start event.
        5. While the queue is not empty:
           - pop the next node from the front of the queue
           - visit each unvisited neighbour in deterministic order
           - record its parent, visited_order, and route from the start
           - emit an expand event and push it onto the queue
           - if the neighbour is the goal, emit found and return
        6. If the loop finishes, emit fail and return not_found
    """
    start = normalise_node_id(graph["start"])
    goal = normalise_node_id(graph["goal"])
    parents = {start: None}
    adjacency = build_adjacency(graph)
    step = 0
    _ = (goal, adjacency, deque)

    trace = [make_trace_event(step, "start", start, None, 0, [start])]
    step += 1


    visited = { start }
    visited_order = []

    """
    S -> HMN -> MNAK -> NAKD -> AKDBK -> KDB
    """

    queue = deque([start])

    while queue:
        node = queue.popleft()
        if node == goal:
            trace.append(make_trace_event(step, "found", node, parents[node], len(queue), list(queue)))
            return {
                "algorithm": "bfs",
                "status": "found",
                "trace": trace,
                "path": reconstruct_path(parents, goal),
                "visited_order": visited_order,
            }

        visited_order.append(node)
        neighbors = get_neighbours(adjacency, node)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                parents[neighbor] = node
                trace.append(make_trace_event(step, "expand", neighbor, node, len(queue), list(queue)))
                step += 1



    return {
        "algorithm": "bfs",
        "status": "not_found",
        "message": "Replace the placeholder code inside solve_bfs with your full BFS implementation.",
        "trace": trace,
        "path": [],
        "visited_order": [start],
    }


if __name__ == "__main__":
    run_graph_bfs_solver(solve_bfs)
