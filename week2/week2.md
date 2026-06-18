# Week 2: Planning with STRIPS

## Exercise 1: Validate and Repair a Plan

1. move(robot, corridor, mail_room)
2. pickup_parcel(robot, parcel, mail_room)
3. move(robot, mail_room, corridor)
4. move(robot, corridor, office_a)
5. pickup_keycard(robot, keycard, office_a)
6. unlock_door(robot, keycard, lab_door, corridor, lab)
7. move(robot, corridor, lab)
8. drop_parcel(robot, parcel, lab)


1. Find the first action in the proposed plan that is not applicable when reached.
preconditions - pickup_keycard's handempty 

2. Name the missing precondition or false fact that makes it illegal.
handempty(robot) is a missing precondition for pickup_keycard(robot, keycard, office_a). The robot's hand is not empty because it is holding the parcel after step 2.


3. Give one valid repaired plan. Try to keep it short, but you do not need to prove that it is the shortest repair.
after 5, move(robot, office_a, corridor)
also ideally first move(robot, corridor, office_a), 

4. In your repaired plan, identify the step where locked(lab_door) is deleted and unlocked(lab_door) is added.

unlock_door(robot, keycard, lab_door, corridor, lab)

5. Does your repaired plan achieve at(parcel, lab)? Explain how the final action makes the goal true.
pre at(robot, lab)
add at(parcel, lab)
final state at(parcel, lab) is true because the robot drops the parcel in the lab in the final step.
