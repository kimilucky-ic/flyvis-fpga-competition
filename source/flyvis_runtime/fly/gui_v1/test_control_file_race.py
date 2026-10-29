"""PC file race only. No sockets, camera, GPU, neural transaction or board."""
import json,threading,time,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from live_protocol import HERE,load,write

class ControlFileRaceTests(unittest.TestCase):
    def test_transient_read_sharing_conflict_retries_only_read(self):
        with patch.object(Path,'read_text',side_effect=[PermissionError('SHARING'),'{"identity":"same"}']) as read,patch('live_protocol.time.sleep') as sleep:
            self.assertEqual(load('CPU_ONLY.json'),{'identity':'same'})
        self.assertEqual(read.call_count,2);sleep.assert_called_once_with(.01)

    def test_persistent_denial_stays_bounded_and_fails_closed(self):
        with patch.object(Path,'read_text',side_effect=PermissionError('persistent')) as read,patch('live_protocol.time.sleep'):
            with self.assertRaises(PermissionError):load('CPU_ONLY.json')
        self.assertEqual(read.call_count,8)

    def test_missing_and_corrupt_identity_are_never_retried_or_cached(self):
        for fault in (FileNotFoundError('missing'),'{bad-json'):
            with patch.object(Path,'read_text',side_effect=fault if isinstance(fault,Exception) else None,return_value=fault) as read,patch('live_protocol.time.sleep') as sleep:
                with self.assertRaises((FileNotFoundError,json.JSONDecodeError)):load('CPU_ONLY.json')
                self.assertEqual(read.call_count,1);sleep.assert_not_called()

    def test_real_concurrent_replace_and_reads_preserve_complete_identity(self):
        root=HERE/'evidence/repeat_workbench_20261018/cpu_file_race'/uuid.uuid4().hex;root.mkdir(parents=True)
        path=root/'heartbeat.json';write(path,dict(identity='CPU_FIXED',counter=0));errors=[]
        def writer():
            try:
                for k in range(300):write(path,dict(identity='CPU_FIXED',counter=k))
            except BaseException as error:errors.append(repr(error))
        thread=threading.Thread(target=writer);thread.start()
        for k in range(1200):
            value=load(path);self.assertEqual(value['identity'],'CPU_FIXED');self.assertIs(type(value['counter']),int)
        thread.join(10);self.assertFalse(thread.is_alive());self.assertEqual(errors,[])

if __name__=='__main__':unittest.main()
