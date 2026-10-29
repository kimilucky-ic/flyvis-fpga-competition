"""GUI-only reuse of file digests. This is a local cache, never acceptance evidence.

Disabled for standalone auditors by default. GUI entry points opt in. A hit needs
the same path, size, times and filesystem identity; changed/missing files rehash
or fail. Full mode always reads bytes. Cache writes never change source files.
"""
import atexit
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parent
VERSION = 'gui-file-digest-cache/v1'
_UNSET = object()


def signature(path):
    s = Path(path).stat()
    return [s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_dev, s.st_ino]


def full_digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class DigestCache:
    def init__(self, path, enabled=False):
        self.path = Path(path)
        self.enabled = enabled
        self.entries = None
        self.dirty = False
        self.lock = threading.RLock()
        self.hits = self.misses = self.hashed_bytes = 0
        self.hash_seconds = 0.

    def _read(self):
        try:
            if self.path.stat().st_size > 16 * 1024 * 1024:
                return {}
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            return raw['entries'] if raw.get('schema') == VERSION and isinstance(raw.get('entries'), dict) else {}
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def digest(self, path):
        p = Path(path)
        before = signature(p)
        key = os.path.normcase(os.path.abspath(os.fspath(p)))
        with self.lock:
            if self.entries is None:
                self.entries = self._read() if self.enabled else {}
            item = self.entries.get(key)
            if self.enabled and isinstance(item, dict) and item.get('signature') == before:
                digest = item.get('sha256')
                if isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest):
                    self.hits += 1
                    return digest
        tick = time.perf_counter()
        digest = full_digest(p)
        if signature(p) != before:
            raise ValueError('Source changed while hashing: ' + p.name)
        with self.lock:
            self.misses += 1
            self.hashed_bytes += before[0]
            self.hash_seconds += time.perf_counter() - tick
            if self.enabled:
                self.entries[key] = dict(signature=before, sha256=digest)
                self.dirty = True
        return digest

    def flush(self):
        with self.lock:
            if not self.enabled or not self.dirty:
                return
            try:
                entries = self._read()
                entries.update(self.entries)
                if len(entries) > 10000:
                    entries = dict(list(entries.items())[-10000:])
                self.path.parent.mkdir(parents=True, exist_ok=True)
                temp = self.path.with_name(self.path.name + '.' + uuid.uuid4().hex + '.tmp')
                temp.write_text(json.dumps(dict(schema=VERSION, entries=entries), separators=(',', ':')), encoding='utf-8')
                os.replace(temp, self.path)
                self.dirty = False
            except OSError:
                # A missing/unwritable cache only means another full check next time.
                pass

    def status(self):
        with self.lock:
            return dict(enabled=self.enabled, hits=self.hits, misses=self.misses,
                        hashed_bytes=self.hashed_bytes, hash_seconds=self.hash_seconds,
                        policy='REUSE_UNCHANGED_FILE_METADATA' if self.enabled else 'FULL_BYTE_HASH',
                        cache_is_acceptance_evidence=False)


_cache = DigestCache(ROOT/'runtime/startup_cache/file_digests.json')


def configure(enabled=True, path=None):
    global _cache
    _cache.flush()
    _cache = DigestCache(path or ROOT/'runtime/startup_cache/file_digests.json', enabled)
    return _cache


def cached_sha256(path):
    return _cache.digest(path)


def flush():
    _cache.flush()


def status():
    return _cache.status()


atexit.register(flush)


class LazyResource:
    """One attempt per process, thread-safe; shutdown never creates a resource."""
    def init__(self, factory, name):
        self.factory, self.name = factory, name
        self.value = _UNSET
        self.error = None
        self.lock = threading.RLock()

    @property
    def loaded(self):
        return self.value is not _UNSET and self.value is not None

    def get(self):
        with self.lock:
            if self.value is _UNSET:
                try:
                    self.value = self.factory()
                except (OSError, ValueError, KeyError, TypeError, AssertionError, ImportError) as error:
                    self.value = None
                    self.error = str(error)
            if self.value is None:
                raise ValueError(self.error or (self.name + ' unavailable'))
            return self.value

    def __bool__(self):
        try:
            return self.get() is not None
        except ValueError:
            return False

    def __getattr__(self, name):
        return getattr(self.get(), name)

    def load_status(self):
        return dict(state='ready' if self.loaded else 'unavailable' if self.value is None else 'not_loaded', error=self.error)
