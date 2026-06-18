from __future__ import annotations

from ai9414.strips import (
    apply_action_signature,
    build_unimplemented_strips_result,
    get_applicable_actions,
    get_initial_facts,
    run_strips_solver,
)


# Complete the three small functions below. The browser connection, local
# /solve server, request validation, grounded STRIPS actions, and visual replay
# are handled by run_strips_solver(...).
#
# Your job is to implement forward STRIPS breadth-first search (BFS). The same
# code should work unchanged for both demos:
#
# - demo strips: move a robot, collect a keycard, unlock a door, deliver a parcel
# - demo blocksworld: pickup, putdown, unstack, and stack blocks
#
# Do not special-case either demo. In both demos, a state is just a list of
# fact tuples. Examples:
#
#     ("at", "robot", "corridor")
#     ("handempty", "robot")
#     ("on", "a", "c")
#     ("clear", "b")
#
# You do not need to write preconditions or effects. Use these helpers:
#
# - get_initial_facts(problem)
# - get_applicable_actions(problem, facts)
# - apply_action_signature(problem, facts, action)


def state_id(facts):
    """
    Return a stable id for a state so BFS can remember visited states.

    Why:
        The same facts can appear in a different order. Sorting avoids treating
        the same state as new just because the list order changed.

    Suggested one-line solution:
        return tuple(sorted(facts))
    """
    return tuple(sorted(facts))


def goal_satisfied(facts, goal):
    """
    Return True only when every goal fact is present in the current state.

    Suggested approach:
        Convert both lists to sets of tuples, then use issubset(...).
    """
    return set(goal).issubset(set(facts))


def solve_planner(problem):

    start = get_initial_facts(problem)
    frontier = [(start, [])]
    visited = {state_id(start)}

    stats = {
        "expanded_states": 0,
        "frontier_peak": 1,
        "generated_states": 1,
    }

    while frontier:
        if len(frontier) > stats["frontier_peak"]:
            stats["frontier_peak"] = len(frontier)

        facts, plan = frontier.pop(0)
        stats["expanded_states"] += 1
        if goal_satisfied(facts, problem["goal"]):
            return {"algorithm": "strips_bfs", "status": "found", "plan": plan, "stats": stats}
        for action in get_applicable_actions(problem, facts):
            next_facts = apply_action_signature(problem, facts, action)
            next_state_id = state_id(next_facts)
            if next_state_id not in visited:
                visited.add(next_state_id)
                frontier.append((next_facts, plan + [action]))
                stats["generated_states"] += 1

    return {"algorithm": "strips_bfs", "status": "not_found", "plan": [], "stats": stats}

if __name__ == "__main__":
    run_strips_solver(solve_planner)
