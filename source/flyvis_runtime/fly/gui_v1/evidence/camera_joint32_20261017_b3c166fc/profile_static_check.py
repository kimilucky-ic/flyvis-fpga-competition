import cProfile,pstats,io,sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hybrid_full485 import Full485Contract
c=Full485Contract();profile=cProfile.Profile();t=time.perf_counter();profile.runcall(c.unchanged);elapsed=time.perf_counter()-t
stream=io.StringIO();pstats.Stats(profile,stream=stream).strip_dirs().sort_stats('cumulative').print_stats(14)
print(json.dumps(dict(evidence='CPU_ONLY_ONE_ORIGINAL_UNCHANGED_CALL_NOT_NEURAL_RUN',elapsed_s=elapsed,contract_paths=len(c.paths),spatial_pins=len(c.spatial.data['pins']),GPU_starts=0,board_connections=0)))
print(stream.getvalue())
