import json

with open('outputs/branch_and_bound/example_op_solution.json') as f:
    data = json.load(f)

steps = data['metadata']['state_history']['steps']
target_profit = data['total_profit']
total_steps = len(steps)

print('Looking for when incumbent profit reached ' + str(target_profit) + '\n')

# Find first step where incumbent reaches target
found = False
for i, step in enumerate(steps):
    if step.get('best_incumbent_profit') == target_profit:
        step_num = step['step_number']
        print('OPTIMAL FOUND AT STEP ' + str(step_num) + '/' + str(total_steps))
        print('  Action: ' + step['action'])
        print('  Route: ' + str(step['route']))
        print('  Incumbent profit: ' + str(step['best_incumbent_profit']))
        print('  Current profit: ' + str(step['current_profit']))
        print('  Decision reason: ' + step['decision_reason'])
        found = True
        break

if not found:
    print('ERROR: Never found target profit in steps!')
    print('\nIncumbent profit progression (first 15 changes):')
    last_inc = None
    count = 0
    for step in steps:
        inc = step.get('best_incumbent_profit')
        if inc != last_inc:
            print('  Step ' + str(step['step_number']) + ': incumbent = ' + str(inc))
            last_inc = inc
            count += 1
            if count >= 15:
                break
