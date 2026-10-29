"""FlyVis native Windows window. Existing viewer and all source data stay read-only."""
import ctypes
import argparse
from ctypes import wintypes
import hashlib
import html
import logging
import os
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
TITLE = "FlyVis 实验台"
RUNTIME = ROOT / "gui_v1/runtime/desktop"


class SingleWindow:
    def init__(self):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel.CreateMutexW.restype = wintypes.HANDLE
        self.kernel.ReleaseMutex.argtypes = [wintypes.HANDLE]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        name = "Local\\FlyVisDesktop_" + hashlib.sha256(str(ROOT).lower().encode()).hexdigest()[:24]
        self.handle = self.kernel.CreateMutexW(None, True, name)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        self.existing = ctypes.get_last_error() == 183

    def focus_existing(self):
        user = ctypes.WinDLL("user32", use_last_error=True)
        user.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        user.FindWindowW.restype = wintypes.HWND
        user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user.SetForegroundWindow.argtypes = [wintypes.HWND]
        window = user.FindWindowW(None, TITLE)
        if window:
            user.ShowWindow(window, 9)
            user.SetForegroundWindow(window)

    def close(self):
        if not self.existing:
            self.kernel.ReleaseMutex(self.handle)
        self.kernel.CloseHandle(self.handle)


def splash(message, detail=""):
    return """<!doctype html><meta charset='utf-8'><style>
    body{margin:0;background:#0b1119;color:#e0eef4;font:18px 'Segoe UI',sans-serif;
    display:grid;place-content:center;min-height:90vh;padding:32px;box-sizing:border-box}
    h1{font-size:32px;color:#51dfdd}p{line-height:1.8}small{color:#9eafbd;overflow-wrap:anywhere}
    </style><h1>FlyVis 实验台</h1><p>""" + html.escape(message) + "</p><small>" + html.escape(detail) + "</small>"


def main(managed_session=None):
    if sys.platform != "win32":
        raise RuntimeError("This desktop entry is for Windows")
    instance = SingleWindow()
    if instance.existing:
        instance.focus_existing()
        instance.close()
        return 2 if managed_session else 0
    backend = None
    try:
        RUNTIME.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=str(RUNTIME / "desktop.log"), encoding="utf-8", level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        # Keep the desktop engine/cache in its own GUI directory.
        os.environ["PYWEBVIEW_GUI"] = "edgechromium"
        import webview
        from desktop_runtime import DesktopBackend, SessionRecord
        record = SessionRecord(RUNTIME)
        if managed_session:
            from desktop_live import ManagedDesktopBackend
            backend = ManagedDesktopBackend(record,managed_session)
        else:
            backend = DesktopBackend(record)
        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.settings["ALLOW_FILE_URLS"] = False
        window = webview.create_window(TITLE, html=splash("正在校验真实实验数据…", "验证完成后自动进入实验界面。"),
                                       width=1400, height=920, min_size=(900, 650),
                                       background_color="#0b1119", text_select=True)

        def load_data():
            try:
                url = backend.start()
                if url and not backend.stop.is_set():
                    window.load_url(url)
            except Exception as error:
                logging.exception("Desktop data startup failed")
                if not backend.stop.is_set():
                    record.write("failed", error=str(error))
                    window.load_html(splash("数据校验或启动失败", f"{error}　日志：{RUNTIME / 'desktop.log'}"))

        def install_desktop_links():
            # Preserve the viewer bytes; desktop-only source links save the original file.
            if backend.url and not backend.stop.is_set() and (window.get_current_url() or "").rstrip("/") == backend.url:
                window.evaluate_js((ROOT / "gui_v1/desktop_links.js").read_text(encoding="utf-8"))
                window.evaluate_js("document.documentElement.dataset.flyvisDisplayHost='WINDOWS_DESKTOP_WEBVIEW2'")

        def watch_owned_stop():
            while not backend.stop.wait(.25):
                if (backend.root/'STOP_REQUEST.json').exists():
                    window.destroy()
                    return

        window.events.closed += backend.close
        window.events.loaded += install_desktop_links
        worker = threading.Thread(target=load_data, daemon=True, name="FlyVis data validation")
        def begin():
            worker.start()
            if managed_session:threading.Thread(target=watch_owned_stop,daemon=True,name='FlyVis desktop close').start()
        webview.start(func=begin, gui="edgechromium", private_mode=False,
                      storage_path=str(RUNTIME / "webview2"), icon=str(ROOT / "gui_v1/desktop.ico"))
        return 0
    except Exception:
        logging.exception("Desktop application failed")
        ctypes.windll.user32.MessageBoxW(None, "桌面程序启动失败。\n请查看 GUI 日志：\n" + str(RUNTIME / "desktop.log"), TITLE, 0x10)
        return 1
    finally:
        if backend is not None:
            backend.close()
        instance.close()


if __name__ == "__main__":
    # pythonw has no console streams; dependencies may write diagnostics to them.
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with (RUNTIME / "engine.log").open("a", encoding="utf-8") as stream:
        sys.stdout = sys.stderr = stream
        parser=argparse.ArgumentParser();parser.add_argument('--managed-session');args=parser.parse_args()
        raise SystemExit(main(args.managed_session))
