import base64
import gzip
import tarfile
import io

with open('setup_server.py', 'r', encoding='utf-8') as f:
    code = f.read()

payload_start = code.find('PAYLOAD = "') + len('PAYLOAD = "')
payload_end = code.find('"', payload_start)
payload_b64 = code[payload_start:payload_end]

buf = io.BytesIO(gzip.decompress(base64.b64decode(payload_b64)))
in_tar = tarfile.open(fileobj=buf)

with open('embedding_model.py', 'rb') as f:
    new_data = f.read()

out_buf = io.BytesIO()
out_tar = tarfile.open(fileobj=out_buf, mode='w')

for m in in_tar.getmembers():
    if m.name == 'components/embedding_model.py':
        ti = tarfile.TarInfo(name=m.name)
        ti.size = len(new_data)
        ti.mtime = m.mtime
        ti.mode = m.mode
        ti.type = m.type
        out_tar.addfile(ti, io.BytesIO(new_data))
    else:
        out_tar.addfile(m, in_tar.extractfile(m))

in_tar.close()
out_tar.close()

new_payload_b64 = base64.b64encode(gzip.compress(out_buf.getvalue())).decode('ascii')
new_code = code[:payload_start] + new_payload_b64 + code[payload_end:]

with open('setup_server.py', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Successfully updated setup_server.py payload!")

