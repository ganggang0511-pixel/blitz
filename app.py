import os, sys, json, base64, random, string, subprocess, threading, time, urllib.request, zipfile, tarfile
from pathlib import Path
from flask import Flask, Response

# ---- obfuscated config ----
_a = os.environ.get('ARGO_DOMAIN', 'mephia.tjzsg.cc.cd')
_b = os.environ.get('ARGO_AUTH', '')
_c = os.environ.get('UUID', ''.join(random.choice('0123456789abcdef') for _ in range(8)) + '-' + ''.join(random.choice('0123456789abcdef') for _ in range(4)) + '-' + ''.join(random.choice('0123456789abcdef') for _ in range(4)) + '-' + ''.join(random.choice('0123456789abcdef') for _ in range(4)) + '-' + ''.join(random.choice('0123456789abcdef') for _ in range(12)))
_d = int(os.environ.get('PORT', '8080'))
_e = int(os.environ.get('ARGO_PORT', '8001'))
_f = Path(os.environ.get('FILE_PATH', '.cache'))
_g = os.environ.get('NAME', 'blitz')
_h = base64.b64decode('aHR0cHM6Ly9naXRodWIuY29tL1hUTFMvWHJheS1jb3JlL3JlbGVhc2VzL2xhdGVzdC9kb3dubG9hZA==').decode()
_i = base64.b64decode('aHR0cHM6Ly9naXRodWIuY29tL2Nsb3VkZmxhcmUvY2xvdWRmbGFyZWQvcmVsZWFzZXMvbGF0ZXN0L2Rvd25sb2Fk').decode()

_f.mkdir(parents=True, exist_ok=True)

def _l(m):
    print(f'[{time.strftime("%H:%M:%S")}] {m}', flush=True)

def _dl(n, u):
    p = _f / n
    try:
        _l(f'DL {n}')
        urllib.request.urlretrieve(u, p)
        os.chmod(p, 0o755)
        return True
    except Exception as ex:
        _l(f'DL fail {n}: {ex}')
        return False

def _arch():
    import platform
    m = platform.machine().lower()
    return 'arm64' if 'aarch64' in m or 'arm' in m else 'amd64'

def _prep():
    a = _arch()
    # xray
    xn = 'x64' if a == 'amd64' else 'a64'
    xu = f'{_h}/Xray-linux-64.zip'
    zp = _f / 'x.zip'
    try:
        urllib.request.urlretrieve(xu, zp)
        with zipfile.ZipFile(zp) as z:
            z.extract('xray', _f)
        os.chmod(_f / 'xray', 0o755)
        zp.unlink()
        _l('xray ok')
    except Exception as ex:
        _l(f'xray fail: {ex}')
        return False
    # cloudflared
    cu = f'{_i}/cloudflared-linux-{a}'
    if not _dl('cfd', cu):
        return False
    _l('cfd ok')
    return True

def _cfg():
    cfg = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": _e,
            "protocol": "vless",
            "settings": {
                "clients": [{"id": _c, "flow": ""}],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "wsSettings": {"path": "/_w"}
            },
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}
        }],
        "outbounds": [
            {"protocol": "freedom", "tag": "direct"},
            {"protocol": "blackhole", "tag": "blocked"}
        ]
    }
    (_f / 'c.json').write_text(json.dumps(cfg))
    _l('cfg ok')

def _run():
    _cfg()
    # xray
    xp = subprocess.Popen([str(_f / 'xray'), 'run', '-c', str(_f / 'c.json')],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _l(f'xray pid {xp.pid}')
    time.sleep(2)
    # cloudflared
    if _b and len(_b) > 100:
        _l('cfd token mode')
        cp = subprocess.Popen([str(_f / 'cfd'), 'tunnel', '--edge-ip-version', 'auto',
                               '--no-autoupdate', '--protocol', 'http2',
                               'run', '--token', _b],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        _l('cfd quick mode')
        cp = subprocess.Popen([str(_f / 'cfd'), 'tunnel', '--url', f'http://localhost:{_e}'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _l(f'cfd pid {cp.pid}')

def _link():
    p = base64.b64encode(f'/_w?ed=2560'.encode()).decode()
    return f'vless://{_c}@{_a}:443?encryption=none&security=tls&sni={_a}&fp=chrome&type=ws&host={_a}&path=%2F_w%3Fed%3D2560#{_g}'

app = Flask(__name__)

@app.route('/')
def _idx():
    return Response('<h3>ok</h3>', mimetype='text/html')

@app.route('/sub')
def _sub():
    lk = _link()
    return Response(base64.b64encode(lk.encode()).decode(), mimetype='text/plain')

@app.route('/list')
def _lst():
    return Response(_link() + '\n', mimetype='text/plain')

if __name__ == '__main__':
    if not _prep():
        _l('prep failed, exit')
        sys.exit(1)
    threading.Thread(target=_run, daemon=True).start()
    time.sleep(3)
    _l(f'sub: {_link()}')
    app.run(host='0.0.0.0', port=_d, threaded=True)
