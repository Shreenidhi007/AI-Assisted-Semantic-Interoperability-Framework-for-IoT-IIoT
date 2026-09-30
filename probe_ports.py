import urllib.request
import urllib.error
import socket

ip = '192.168.0.21'
ports = [22, 80, 1883, 5000, 5432, 8008, 8080, 8081]

for port in ports:
    print('--- Port', port, '---')
    try:
        url = 'http://' + ip + ':' + str(port) + '/'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as resp:
            srv = resp.headers.get('Server', 'unknown')
            ct = resp.headers.get('Content-Type', 'unknown')
            print('HTTP', resp.getcode(), '| Server:', srv, '| Type:', ct)
            data = resp.read(150)
            print('Snippet:', data[:100])
    except urllib.error.HTTPError as e:
        srv = e.headers.get('Server', 'unknown') if e.headers else 'unknown'
        print('HTTP Error', e.code, '| Server:', srv)
    except Exception as e:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5)
                s.connect((ip, port))
                banner = s.recv(100)
                print('Banner:', banner)
        except Exception as e2:
            print('Non-HTTP/Raw error:', e2)

