#!/usr/bin/env python3
"""
Inspect and repair corrupted/smashed lines in data/output/enviromap_kg.ttl
"""

import sys
import re
from rdflib import Graph

path = "data/output/enviromap_kg.ttl"
print(f"Reading {path}...")

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines):,}")

# Inspect around line 142593
start_idx = max(0, 142593 - 8)
end_idx = min(len(lines), 142593 + 8)

print("\n--- Inspecting lines around 142593 ---")
for i in range(start_idx, end_idx):
    print(f"{i+1}: {repr(lines[i])}")

# Search for any broken occurrences of 'Hydroponics W'
fixed_count = 0
for i in range(len(lines)):
    if 'Hydroponics W' in lines[i] and 'ater Temperature Sensor' not in lines[i]:
        print(f"\nFound broken line at {i+1}: {repr(lines[i])}")
        # Look at next line
        if i + 1 < len(lines):
            print(f"Next line {i+2}: {repr(lines[i+1])}")
            # Replace with valid line
            lines[i] = '    rdfs:label "Hydroponics Water Temperature Sensor" ;\n'
            # If the next line had the rest of the string, fix it
            if 'ater Temperature Sensor' in lines[i+1]:
                # Remove the broken fragment from next line
                lines[i+1] = re.sub(r'.*?ater Temperature Sensor.*?;', '', lines[i+1]).lstrip()
                if not lines[i+1].strip():
                    lines[i+1] = ''
            fixed_count += 1

    # Also check if 'Water Temperature Sensor' was smashed on a single line
    elif 'rdfs:label "Hydroponics W' in lines[i]:
        print(f"\nFound smashed label on line {i+1}: {repr(lines[i])}")
        lines[i] = re.sub(r'rdfs:label\s+"Hydroponics\s+W[^"]*ater\s+Temperature\s+Sensor"\s*;', 'rdfs:label "Hydroponics Water Temperature Sensor" ;', lines[i])
        fixed_count += 1

# Write back if fixed
if fixed_count > 0:
    print(f"\nWriting {fixed_count} fix(es) to {path}...")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines([line for line in lines if line])
    print("✅ File written!")
else:
    # Direct text replacement fallback
    print("\nScanning full text for bad fragments...")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Search regex for broken label
    bad_pattern = re.compile(r'rdfs:label\s+"Hydroponics\s+W[^"]*?"\s*;\s*sosa:isHostedBy', re.DOTALL)
    if bad_pattern.search(text):
        print("Found matching bad pattern in text! Replacing...")
        text = bad_pattern.sub('rdfs:label "Hydroponics Water Temperature Sensor" ;\n    sosa:isHostedBy', text)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("✅ Replaced via pattern match!")
    else:
        print("Pattern not matched directly. Checking parser...")

print("\n--- Validating Knowledge Graph with RDFLib ---")
try:
    g = Graph()
    g.parse(path, format="turtle")
    print(f"🎉 SUCCESS! Knowledge Graph parsed completely: {len(g):,} triples loaded!")
except Exception as e:
    print(f"❌ RDFLib Parser Error: {e}")

