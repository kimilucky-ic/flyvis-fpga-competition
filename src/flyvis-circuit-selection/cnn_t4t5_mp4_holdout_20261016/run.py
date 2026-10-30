"""Use accepted runner function unchanged, binding this campaign's paths."""
from core import *
import uuid

execute_accepted_function(PREVIOUS/'run.py','main',globals())

if __name__=='__main__':
    try:
        for case in load(HERE/'INPUTS.json'):
            assert sha(case['video_path'])==case['video_sha256']
        main()
    except BaseException as exc:
        dump(HERE/('FAILURE_run_'+str(time.time_ns())+'.json'),dict(error=repr(exc),retry=False)); raise
