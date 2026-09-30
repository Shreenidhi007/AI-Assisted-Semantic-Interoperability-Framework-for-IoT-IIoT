import base64
import io
import tarfile

with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\setup_server.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

marker = 'PAYLOAD = """'
idx1 = text.find(marker)
if idx1 != -1:
    idx1 += len(marker)
    idx2 = text.find('"""', idx1)
    payload_str = text[idx1:idx2].strip()
    tar_bytes = base64.b64decode(payload_str)
    tar_buf = io.BytesIO(tar_bytes)
    with tarfile.open(fileobj=tar_buf, mode='r:gz') as tar:
        names = tar.getnames()
        print(f"Total files in setup_server archive: {len(names)}")
        for n in sorted(names):
            print(f"  - {n}")
else:
    print("Marker not found")

