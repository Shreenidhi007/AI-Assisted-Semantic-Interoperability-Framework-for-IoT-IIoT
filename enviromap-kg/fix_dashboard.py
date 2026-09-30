path = r'C:\Users\Shreenithi\.gemini\antigravity\scratch\enviromap-kg\scripts\dashboard.py'
with open(path, encoding='utf-8') as f:
    c = f.read()
c = c.replace('use_container_width=True', 'width="stretch"')
c = c.replace('use_container_width=False', 'width="content"')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Fixed! Count:', c.count('width="stretch"'), 'replacements.')

