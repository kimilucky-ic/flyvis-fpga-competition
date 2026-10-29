"""Owned local HTTP backend for the desktop window; no device/model imports."""
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
from time import perf_counter
import uuid

from data_store import DataStore, ROOT
from server import handler_factory


class SessionRecord:
    def init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.started = perf_counter()
        self.id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        self.path = self.folder / (self.id + ".json")
        self.data = {"schema": "flyvis-desktop-session-v1", "session_id": self.id,
                     "pid": os.getpid(), "root": str(ROOT), "backend_owned_by_window": True,
                     "execution_kind": "offline_replay", "events": []}
        self.write("starting")

    def write(self, phase, **fields):
        with self.lock:
            self.data.update(fields, phase=phase)
            self.data["events"].append({"phase": phase, "utc": datetime.now(timezone.utc).isoformat(),
                                        "elapsed_s": perf_counter() - self.started})
            encoded = json.dumps(self.data, ensure_ascii=False, indent=2)
            for target in [self.path, self.folder / "current.json"]:
                temporary = target.with_suffix(".json.tmp")
                temporary.write_text(encoded, encoding="utf-8")
                temporary.replace(target)


class DesktopBackend:
    """Bind an OS-assigned loopback port and close only this instance's server.

    Validation can be cancelled before it completes. The stop flag and ownership
    lock prevent a late validator from creating a server after the window closes.
    """
    def init__(self, record, factory=DataStore):
        self.record, self.factory = record, factory
        self.stop = threading.Event()
        self.ownership = threading.RLock()
        self.cleanup = threading.Lock()
        self.server = self.thread = None
        self.url = None
        self.stopped = False

    def start(self):
        with self.ownership:
            if self.stop.is_set():
                return None
            self.record.write("validating")
        store = self.factory()
        with self.ownership:
            if self.stop.is_set():
                return None
            handler = handler_factory(store)

            class QuietHandler(handler):
                def log_message(self, *args):
                    pass

            server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
            server.daemon_threads = True
            self.server = server
            self.url = f"http://127.0.0.1:{server.server_port}"
            self.thread = threading.Thread(target=server.serve_forever,
                                           kwargs={"poll_interval": .1}, daemon=True,
                                           name="FlyVis desktop HTTP")
            self.thread.start()
            catalog = store.catalog()
            self.record.write("ready", url=self.url, port=server.server_port,
                              datasets={d["id"]: len(d["conditions"]) for d in catalog["datasets"]},
                              conditions=sum(len(d["conditions"]) for d in catalog["datasets"]),
                              unavailable_datasets=catalog["unavailable_datasets"],
                              gpu_service="not_connected")
        return self.url

    def close(self):
        self.stop.set()
        with self.cleanup:
            if self.stopped:
                return
            with self.ownership:
                server, thread = self.server, self.thread
                self.server = None
            if server is not None:
                server.shutdown()
                server.RequestHandlerClass.close_camera()
                server.server_close()
                thread.join(timeout=3)
                if thread.is_alive():
                    raise RuntimeError("Owned desktop HTTP thread did not exit")
            self.stopped = True
            self.record.write("closed", backend_stopped=True)
