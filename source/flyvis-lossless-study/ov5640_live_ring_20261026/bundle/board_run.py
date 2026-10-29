"""Legacy single-frame entry disabled for ring release; use live_board.run."""
def execute(*args,**kwargs):
    raise RuntimeError("Use the dedicated ring60s Notebook; no legacy one-frame hardware entry")
