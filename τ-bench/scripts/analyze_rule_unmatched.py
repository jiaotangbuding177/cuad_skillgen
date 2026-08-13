import json
from collections import Counter

data = json.loads(open('results/evaluation/atom_extraction_llm_comparison.json', encoding='utf-8').read())
atoms = data['comparison']['rule_unmatched_atoms']

origin_counts = Counter(a['origin'] for a in atoms)
type_counts = Counter(a['type'] for a in atoms)

print(f'Total: {len(atoms)} atoms\n')

print('=== By origin ===')
for origin, count in sorted(origin_counts.items(), key=lambda x: -x[1]):
    print(f'  {origin}: {count}')

print('\n=== By type ===')
for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f'  {t}: {count}')

print('\n=== High-value candidates (warnings, validation, checks) ===')
keywords = ['warning', 'does not check', 'must be valid', 'max 6 months', 'raises', 'valueerror', 'check the bill', 'already paid', 'not active', 'not found']
high_value = [a for a in atoms if any(kw in a['text'].lower() for kw in keywords)]
print(f'Found: {len(high_value)} atoms\n')
for a in high_value:
    origin = a['origin']
    subj = a['subject']
    text = a['text'][:120]
    atype = a['type']
    print(f'  [{atype}] ({origin}) {subj}: {text}')

print('\n=== Tool schema required_input (parameter requirements) ===')
schema_inputs = [a for a in atoms if a['origin'] == 'tool_schema' and a['type'] == 'required_input']
print(f'Count: {len(schema_inputs)}\n')
for a in schema_inputs:
    print(f'  {a["subject"]}: {a["text"]}')

print('\n=== Actor constraint (tool ownership) ===')
actor = [a for a in atoms if a['type'] == 'actor_constraint' and 'owned by' in a['text']]
print(f'Count: {len(actor)}\n')
for a in actor[:5]:
    print(f'  {a["subject"]}: {a["text"]}')

print('\n=== Policy text (not from tools) ===')
policy = [a for a in atoms if a['origin'] == 'policy']
print(f'Count: {len(policy)}\n')
for a in policy:
    print(f'  [{a["type"]}] {a["subject"]}: {a["text"][:100]}')
