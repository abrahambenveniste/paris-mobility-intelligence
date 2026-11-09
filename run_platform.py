"""Run the integrated local tool and collectors; Ctrl+C stops owned processes."""
import argparse
from contextlib import closing
import json
import subprocess
import sys
import time
from urllib.request import urlopen
import webbrowser
from app import ROOT


def ready():
    try:
        with urlopen('http://127.0.0.1:8765/api/network',timeout=2) as response:
            return json.load(response).get('scope') == 'metro'
    except Exception:
        return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--with-predictions',action='store_true',help='Also run the existing two-point line-4 prediction pilot')
    args=parser.parse_args()
    from disruption_history import connect
    with closing(connect()):
        pass  # Migrate older line-4 archives before the read-only website opens.
    children=[]
    try:
        if not ready():
            server=subprocess.Popen([sys.executable,str(ROOT/'app.py')],cwd=ROOT)
            children.append(server)
            for _ in range(20):
                if ready():
                    break
                if server.poll() is not None:
                    raise RuntimeError('Explorer could not start. Check its message above.')
                time.sleep(1)
            else:
                raise RuntimeError('Explorer did not become available.')
        children.append(subprocess.Popen([sys.executable,str(ROOT/'disruption_history.py')],cwd=ROOT))
        if args.with_predictions:
            children.append(subprocess.Popen([sys.executable,str(ROOT/'collect.py')],cwd=ROOT))
        webbrowser.open('http://127.0.0.1:8765/history')
        print('Platform running. Ctrl+C stops collectors started here. Existing explorer windows remain yours.',flush=True)
        while True:
            if any(child.poll() is not None for child in children):
                raise RuntimeError('A platform process stopped. Review its message above and restart.')
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping platform processes.')
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            child.wait(timeout=10)


if __name__=='__main__':
    main()
