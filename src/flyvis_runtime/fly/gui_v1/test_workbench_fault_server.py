"""Isolated browser failure test; real sources are read-only, no activity is created."""
import argparse
from http.server import ThreadingHTTPServer
from data_store import DataStore
from server import handler_factory


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8772);args=parser.parse_args()
    parent=handler_factory(DataStore())
    class FaultHandler(parent):
        def do_GET(self):
            if self.path.startswith('/api/workbench/runs/') and self.path.endswith('/activity.bin'):
                return self.send({'status':'NOT_AVAILABLE','result':None,'error':'TEST_ONLY: workbench source intentionally unavailable; no source changed'},status=409)
            return super().do_GET()
    with ThreadingHTTPServer(('127.0.0.1',args.port),FaultHandler) as server:
        print(f'TEST_ONLY workbench source failure: http://127.0.0.1:{args.port}',flush=True)
        server.serve_forever()


if __name__=='__main__':main()
