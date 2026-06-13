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
    # Iterative Depth-First Search (DFS) using a stack (LIFO).
    #
    # How it works visually:
    #
    #   Stack grows downward. We always look at the TOP (last element).
    #
    #   Step 0 (start):     stack = [S]
    #                       Peek at S. It's not the goal.
    #
    #   Step 1 (expand H):  stack = [S, H]
    #                       S's first unvisited neighbour is H. Push H.
    #                       The graph highlights the S -> H edge.
    #
    #   Step 2 (expand E):  stack = [S, H, E]
    #                       H's first unvisited neighbour is E. Push E.
    #                       DFS dives deeper — always going down one branch.
    #
    #   Step 3 (backtrack): stack = [S, H]
    #                       E has no unvisited neighbours — dead end!
    #                       Pop E off. We retreat back to H to try another branch.
    #
    #   Step 4 (expand K):  stack = [S, H, K]
    #                       H's next unvisited neighbour is K. Push K.
    #                       DFS tries the next branch from H.
    #
    #   ... continues until goal is found or stack is empty.
    #
    #   Key idea: DFS explores as DEEP as possible before backtracking.
    #   The stack represents the current path from start to the active node.
    #   depth = len(stack) - 1  (start node is depth 0).

    start = normalise_node_id(graph["start"])
    goal = normalise_node_id(graph["goal"])
    adjacency = build_adjacency(graph)

    # datastructures
    stack = [start]  # the DFS frontier — current path from start
    visited = {start}  # nodes we've already seen (never revisit)
    parents = {start: None}  # parent pointers for path reconstruction
    visited_order = [start]  # discovery order for the trace
    trace = []
    step = 0

    # Emit the initial "start" event — we're at the start node, depth 0
    trace.append(make_trace_event(step, "start", start, None, 0, stack))
    step += 1

    while stack:
        current = stack[-1]  # peek at the top — this is our current node

        # Goal check: if the top of the stack is the goal, we're done
        if current == goal:
            trace.append(make_trace_event(step, "found", current, parents[current], len(stack) - 1, stack))
            return {
                "algorithm": "dfs",
                "status": "found",
                "trace": trace,
                "path": reconstruct_path(parents, goal),
                "visited_order": visited_order,
            }

        # Find the first unvisited neighbour (sorted order for determinism)
        neighbors = get_neighbours(adjacency, current)
        next_node = None
        for n in neighbors:
            if n not in visited:
                next_node = n
                break  # DFS only takes the FIRST unvisited neighbour

        if next_node is not None:
            # EXPAND: push the neighbour and go deeper
            stack.append(next_node)
            visited.add(next_node)
            parents[next_node] = current
            visited_order.append(next_node)
            trace.append(make_trace_event(step, "expand", next_node, current, len(stack) - 1, stack))
            step += 1

        else:
            # BACKTRACK: no unvisited neighbours — dead end, pop and retreat
            stack.pop()
            trace.append(make_trace_event(step, "backtrack", current, parents[current], len(stack) - 1, stack))
            step += 1

    # Stack is empty — we explored everything reachable and never found the goal
    trace.append(make_trace_event(step, "fail", None, None, 0, []))
    return {
        "algorithm": "dfs",
        "status": "not_found",
        "trace": trace,
        "path": [],
        "visited_order": visited_order,
    }


if __name__ == "__main__":
    run_graph_solver(solve_dfs)
