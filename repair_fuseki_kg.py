#!/usr/bin/env python3
"""
Target exact line (len - 187) and inspect the corrupt token.
"""
import os
import sys
import re

ttl_path = os.path.expanduser("~/semantic-interoperability-kg/data/output/enviromap_kg.ttl")

if not os.path.exists(ttl_path):
    print(f"Error: {ttl_path} does not exist.")
    sys.exit(1)

with open(ttl_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

total = len(lines)
print(f"Total lines in file: {total:,}")

target_from_end = 187
target_line_idx = total - target_from_end
print(f"Inspecting target line ~{target_line_idx + 1} (offset -{target_from_end} from end)...")

start = max(0, target_line_idx - 15)
end = min(total, target_line_idx + 15)

print(f"\n--- Context around lines {start+1} to {end} ---")
for idx in range(start, end):
    lineno = idx + 1
    marker = ">>> " if lineno == (target_line_idx + 1) else "    "
    print(f"{marker}{lineno:7d}: {repr(lines[idx])}")

# Search for any line in the whole file that has "-9" in column 1 to 10
found_instances = []
for idx, line in enumerate(lines):
    # Check if there is -9 near the start of the line (ignoring whitespace)
    lstrip = line.lstrip()
    if lstrip.startswith("-9") or lstrip.startswith("-1") or lstrip.startswith("-"):
        # Check if it doesn't have a colon or http (i.e. not a predicate)
        if not lstrip.startswith("--") and ":" not in lstrip.split()[0] and not lstrip.startswith("<"):
            found_instances.append((idx + 1, line))

print(f"\nFound {len(found_instances)} lines starting with negative numbers without predicate:")
for lineno, l in found_instances:
    print(f"Line {lineno}: {repr(l)}")

# Let's fix them:
fixed_lines = []
fix_count = 0
for idx, line in enumerate(lines):
    lstrip = line.lstrip()
    if (lstrip.startswith("-9") or lstrip.startswith("-1") or lstrip.startswith("-")) and (not lstrip.startswith("--") and ":" not in lstrip.split()[0] and not lstrip.startswith("<")):
        # Extract the number and terminator
        val = lstrip.strip().rstrip(";").rstrip(".").rstrip(",")
        term = ";"
        if lstrip.strip().endswith("."):
            term = "."
        elif lstrip.strip().endswith(","):
            term = ","
        
        # Replace with valid predicate
        repaired = f'            saref:hasValue "{val}"^^xsd:float {term}\n'
        print(f"Fixing line {idx+1}: {repr(line)} -> {repr(repaired)}")
        fixed_lines.append(repaired)
        fix_count += 1
    else:
        fixed_lines.append(line)

if fix_count > 0:
    backup_path = ttl_path + ".bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    with open(ttl_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)
    print(f"\nSUCCESS: Applied {fix_count} fix(es) to {ttl_path}!")
else:
    print("\nCould not automatically find lines starting with negative numbers. Checking if any line has '-9' anywhere...")
    for idx in range(max(0, target_line_idx - 25), min(total, target_line_idx + 25)):
        if "-9" in lines[idx]:
            print(f"Line {idx+1}: {repr(lines[idx])}")

