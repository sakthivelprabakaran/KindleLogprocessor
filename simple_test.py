import re

sample_data = '''
ITERATION_01
Some log line 1
Some log line 2

ITERATION_02
Some log line 3
Some log line 4
'''

print('Testing iteration splitting...')
print('Sample data:')
print(repr(sample_data))
print()

iterations = re.split(r'ITERATION_(\d+)', sample_data)[1:]
print(f'Found {len(iterations)} parts after split')

for i, part in enumerate(iterations):
    print(f'Part {i}: {repr(part[:30])}...')

iteration_pairs = []
for i in range(0, len(iterations), 2):
    if i+1 < len(iterations):
        iteration_num = iterations[i]
        iteration_content = iterations[i+1]
        iteration_pairs.append((iteration_num, iteration_content))

print(f'\nCreated {len(iteration_pairs)} iteration pairs')
for num, content in iteration_pairs:
    print(f'  Iteration {num}: {len(content.strip())} chars')
    print(f'    Content preview: {repr(content.strip()[:50])}...')