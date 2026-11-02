"""Session-scoped allocation target for the pinned official camera cache.
No global PYNQ monkey patch. Original getframe bytecode and cache semantics run
with only its allocate global bound to the already resolved memory object.
"""
import types
class CameraMemory:
    def __init__(self,channel):
        cache=channel._cache;original=cache.getframe
        if 'getframe' in cache.__dict__ or not isinstance(original,types.MethodType):
            raise RuntimeError('camera cache already adapted or unexpected method')
        if 'allocate' not in original.__func__.__globals__:raise RuntimeError('missing official allocator')
        self.channel,self.cache,self.original=channel,cache,original
        self.device=channel._mmio.device
        self.target=self.device.default_memory # exactly once, after overlay load/configure
        if not callable(getattr(self.target,'allocate',None)):raise RuntimeError('invalid camera memory target')
        self.active=True;self.failed=False;self.calls=0
        allocate=original.__func__.__globals__['allocate']
        def bound_allocate(*args,**kwargs):
            if not self.active or self.failed or channel._cache is not cache or channel._mmio.device is not self.device:
                raise RuntimeError('stale camera allocation session; no retry')
            if kwargs.get('target') is not None:raise RuntimeError('unexpected existing allocator target')
            kwargs['target']=self.target
            try:
                value=allocate(*args,**kwargs);self.calls+=1;return value
            except BaseException:
                self.failed=True;raise
        environment=dict(original.__func__.__globals__);environment['allocate']=bound_allocate
        fn=types.FunctionType(original.__func__.__code__,environment,original.__func__.__name__,
                              original.__func__.__defaults__,original.__func__.__closure__)
        fn.__kwdefaults__=original.__func__.__kwdefaults__
        bound=types.MethodType(fn,cache)
        def getframe(owned_cache):
            if not self.active or self.failed or channel._cache is not cache or channel._mmio.device is not self.device:
                raise RuntimeError('stale camera cache session')
            return bound()
        cache.getframe=types.MethodType(getframe,cache)
    def close(self):self.active=False
    def summary(self):
        return dict(default_memory_resolutions=1,frame_allocations=self.calls,active=self.active,failed=self.failed,
            scope='one video cache instance and current overlay session; exclusive ownership required')
