import time
import os
import sys
from prometheus_client import start_http_server

# ensure project root is on path for imports
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from monitoring.metrics import configure_from_env

def main():
    cfg = configure_from_env()
    port = cfg.get('metrics_port', 8002)
    start_http_server(port)
    print(f"Prometheus metrics server started on :{port}")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Metrics server stopping")

if __name__ == '__main__':
    main()
