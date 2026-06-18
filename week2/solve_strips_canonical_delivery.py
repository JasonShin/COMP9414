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
    raise NotImplementedError("TODO: implement state_id")


def goal_satisfied(facts, goal):
    """
    Return True only when every goal fact is present in the current state.

    Suggested approach:
        Convert both lists to sets of tuples, then use issubset(...).
    """
    raise NotImplementedError("TODO: implement goal_satisfied")


def solve_planner(problem):
    """
    Run forward STRIPS BFS.

    Each frontier item is:

        (facts, plan)

    where facts is the current state and plan is the list of action strings
    used to reach it.
    """
    start = get_initial_facts(problem)
    frontier = [(start, [])]
    visited = {state_id(start)}

    print("checking problem:", problem)
    # TODO:
    # Replace this placeholder with the BFS loop.
    #
    # Pseudocode:
    # while frontier is not empty:
    #     remove the first (facts, plan) pair from frontier
    #     if facts satisfy problem["goal"], return:
    #         {"algorithm": "strips_bfs", "status": "found", "plan": plan}
    #     for each applicable action:
    #         next_facts = apply_action_signature(problem, facts, action)
    #         if next_facts has not been visited:
    #             remember it
    #             add (next_facts, plan + [action]) to the frontier
    #
    # If the loop finishes, return:
    #     {"algorithm": "strips_bfs", "status": "not_found", "plan": []}
    _ = (frontier, visited)

    return build_unimplemented_strips_result("TODO: implement forward STRIPS BFS planning.")


if __name__ == "__main__":
    run_strips_solver(solve_planner)
