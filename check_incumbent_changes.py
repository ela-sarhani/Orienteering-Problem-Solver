import json

with open('outputs/branch_and_bound/example_op_solution.json') as f:
    data = json.load(f)

steps = data['metadata']['state_history']['steps']

print('Incumbent profit changes throughout algorithm:\n')

last_inc = None
changes = []

for step in steps:
    inc = step.get('best_incumbent_profit')
    if inc != last_inc:
        changes.append((step['step_number'], last_inc, inc))
        last_inc = inc

if len(changes) == 1:
    print('  Only 1 incumbent value throughout: ' + str(changes[0][2]))
    print('  Set at step ' + str(changes[0][0]) + ' (from greedy initialization)')
    print('\nThis means the greedy completion found the OPTIMAL solution immediately!')
    print('The B&B algorithm then spent 673 steps verifying it was optimal.')
else:
    print('  Incumbent changed ' + str(len(changes)) + ' times:')
    for step_num, old_val, new_val in changes[:10]:
        print('    Step ' + str(step_num) + ': ' + str(old_val) + ' -> ' + str(new_val))
