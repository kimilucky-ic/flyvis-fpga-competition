"""Browser acceptance fixture only: inject HTTP failures, never neural data.

Runs a separately named loopback test server. Does not change source files or
the production launcher's service. Ctrl+C releases this fixture's own port.
"""
import argparse
from copy import deepcopy
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile

from data_store import DataStore, ROOT, read_json
from server import handler_factory


def main():
    parser = argparse.ArgumentParser(description="GUI browser fault acceptance fixture")
    parser.add_argument("--port", type=int, default=8772)
    parser.add_argument("--missing-import", action="store_true")
    parser.add_argument("--fault-target", choices=["camera1", "controlled6"], default="camera1")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="flyvis-gui-browser-fault-") as temporary:
        config = deepcopy(read_json(ROOT / "gui_v1/integrations.json"))
        if args.missing_import:
            config["camera"]["pins"][config["camera"]["handoff"]] = "0" * 64
        path = Path(temporary) / "integrations.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        store = DataStore(integrations_path=path)
        base = handler_factory(store)

        class FaultHandler(base):
            def do_GET(self):
                if self.path == "/api/adapters":
                    return self.send({"status": "not_connected", "error": "TEST FIXTURE: adapter status failure"}, status=503)
                if self.path.startswith(f"/api/datasets/{args.fault_target}/") and "/frames/" in self.path:
                    return self.send({"status": "unavailable", "error": "TEST FIXTURE: original frame temporarily unavailable"}, status=409)
                return super().do_GET()

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", args.port), FaultHandler)
        print(f"TEST FIXTURE ONLY: http://127.0.0.1:{args.port} | real data, injected HTTP failures", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
