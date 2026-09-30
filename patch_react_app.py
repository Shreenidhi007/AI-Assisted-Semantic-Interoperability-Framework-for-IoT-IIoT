#!/usr/bin/env python3
"""
Cleanly fix:
1. Hardcoded :8001 port bug in react-dashboard/src/App.jsx (so frontend uses relative /api)
2. JSX syntax nesting for TabAnalytics & GraphRAGTab
3. React hook imports
"""

import os
import sys
import re

app_path = "src/App.jsx"
if not os.path.exists(app_path):
    print(f"Error: {app_path} not found in {os.getcwd()}")
    sys.exit(1)

with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

print(f"Read {app_path} ({len(code)} chars)")

# Backup original
with open("src/App.jsx.bak", "w", encoding="utf-8") as f:
    f.write(code)

# 1. FIX THE :8001 PORT BUG (The reason for all N/A and 0 values!)
if ":8001" in code:
    print("Found :8001 port in API URL definition! Fixing to relative path...")
    pat_8001 = re.compile(
        r'window\.location\.origin\.includes\([^\)]*\)\s*\?\s*[`\'\"][^`\'\"]*8001[^`\'\"]*[`\'\"]\s*:\s*[`\'\"][^`\'\"]*[`\'\"]'
    )
    if pat_8001.search(code):
        code = pat_8001.sub('""', code)
        print("✅ Fixed API_BASE to relative \"\" (uses NGINX /api/ proxy)")
    else:
        # Fallback replacement
        code = re.sub(r'[`\'\"]http://\$\{[^}]*hostname\}:8001[`\'\"]', '""', code)
        code = code.replace(':8001', '')
        print("✅ Replaced :8001 occurrences")

# 2. FIX THE JSX SYNTAX ERROR
# Pattern 1: Nested TabAnalytics inside Tab 4 or Tab 4 inside TabAnalytics
pat1 = re.compile(
    r'\{activeTab\s*===\s*3\s*&&\s*<TabAnalytics(?:\s+records=\{[^\}]*\}\s*)?[\r\n\s]*\{activeTab\s*===\s*4\s*&&\s*<GraphRAGTab\s*/>\}\s*/>\}',
    re.DOTALL
)

fixed_jsx = False
if pat1.search(code):
    print("Found broken nested TabAnalytics/GraphRAGTab pattern. Fixing...")
    code = pat1.sub(
        '{activeTab === 3 && <TabAnalytics records={kgData?.records || []} />}\n                {activeTab === 4 && <GraphRAGTab />}',
        code
    )
    fixed_jsx = True

# Also check if TabAnalytics wasn't closed before GraphRAGTab:
pat2 = re.compile(
    r'(<TabAnalytics[^>]*?)([\r\n\s]*\{activeTab\s*===\s*4\s*&&\s*<GraphRAGTab\s*/>\}\s*/>\})',
    re.DOTALL
)
if not fixed_jsx and pat2.search(code):
    print("Found broken pattern 2. Fixing...")
    code = pat2.sub(r'\1 />}\n                {activeTab === 4 && <GraphRAGTab />}', code)
    fixed_jsx = True

# Direct string replacement fallback
bad_str = "{activeTab === 3 && <TabAnalytics records={kgData?.records || []}\n            {activeTab === 4 && <GraphRAGTab />} />}"
good_str = "{activeTab === 3 && <TabAnalytics records={kgData?.records || []} />}\n                {activeTab === 4 && <GraphRAGTab />}"
if bad_str in code:
    code = code.replace(bad_str, good_str)
    fixed_jsx = True
    print("Replaced via direct string match!")

bad_str_crlf = "{activeTab === 3 && <TabAnalytics records={kgData?.records || []}\r\n            {activeTab === 4 && <GraphRAGTab />} />}"
if bad_str_crlf in code:
    code = code.replace(bad_str_crlf, good_str)
    fixed_jsx = True
    print("Replaced via CRLF direct string match!")

# 3. ENSURE REACT IS IMPORTED FOR GraphRAGTab
if "React.useState" in code and "import React" not in code:
    print("Ensuring React is imported...")
    if "from 'react'" in code:
        code = re.sub(r'import\s*\{', 'import React, {', code, count=1)
    elif 'from "react"' in code:
        code = re.sub(r'import\s*\{', 'import React, {', code, count=1)
    else:
        code = "import React from 'react';\n" + code

with open(app_path, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Successfully patched src/App.jsx!")
print("🚀 Ready to build: run 'npm run build'")
