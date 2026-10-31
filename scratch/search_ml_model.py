import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['model', 'Model', 'classify', 'DecisionTree', 'joblib', 'pickle', 'predict']):
        print(f"{i+1}: {l.rstrip()}")

