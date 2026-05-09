import json

with open('outputs/branch_and_bound/example_op_solution.json') as f:
    data = json.load(f)

steps = data['metadata']['state_history']['steps']
best_profit = 22.0

print('Looking for steps with complete route (returns to 0) and best profit...\n')

found = False
for step in steps:
    route = step.get('route', [])
    profit = step.get('best_incumbent_profit')
    current_profit = step.get('current_profit')
    
    # Check if route is complete (starts at 0 and ends at 0)
    if len(route) >= 2 and route[0] == 0 and route[-1] == 0:
        if profit == best_profit or current_profit == best_profit:
            print('Step ' + str(step['step_number']) + ':')
            print('  Route: ' + str(route))
            print('  Incumbent profit: ' + str(profit))
            print('  Current profit: ' + str(current_profit))
            print('  Action: ' + step['action'])
            print()
            found = True

if not found:
    print('No complete routes with profit 22.0 found in state history.')
    print('\nThis suggests the greedy solution was found during initialization.')
    print('Final solution: ' + str(data['route']))
    print('Final profit: ' + str(data['total_profit']))
