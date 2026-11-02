"""File-only retry worker. This module has no route to MMIO or neural STEP."""
import json,threading,time,urllib.request,urllib.error
from pathlib import Path
from live_protocol import sha,canonical,atomic,load_packet

def request(config,route,data=None):
    req=urllib.request.Request(config['pc_url']+route,data=data,headers={'Authorization':'Bearer '+config['token'],'Content-Type':'application/octet-stream'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=3) as r:
        if r.status!=200:raise RuntimeError('receiver status '+str(r.status))
        return json.loads(r.read(65536))

class Uploader:
    def __init__(self,out,config,send=request):
        self.out=Path(out);self.config=config;self.send=send;self.stop=threading.Event();self.done=threading.Event();self.thread=None
        self.wake=threading.Event();self.digests={};self.ack_timings={}
        self.cached=None;self.next=0;self.error=None;self.fatal=False;self.finish_sent=False
    def start(self):
        self.thread=threading.Thread(target=self.run,name='line11-file-upload',daemon=True);self.thread.start()
    def attempt(self):
        p=self.out/'transport'/('%06d.packet'%self.next)
        if self.cached is None:
            start=time.monotonic();data=load_packet(self.out,self.next)
            if data is not None:self.cached=(data,time.monotonic()-start,self.digests.get(self.next) or sha(data))
        if self.cached is not None:
            data,rebuild_s,digest=self.cached;t=time.monotonic();a=self.send(self.config,'/ingest',data)
            if a.get('step_id')!=self.next or a.get('sha256')!=digest or a.get('durable') is not True:raise ValueError('bad ACK; no compute retry')
            # Packet itself is already durably acknowledged by PC; save timing metadata once in final receipt.
            self.ack_timings[self.next]=dict(a,round_trip_seconds=time.monotonic()-t,rebuild_seconds=rebuild_s)
            self.next+=1;self.cached=None;self.error=None;return True
        f=self.out/'FINISH.json'
        if self.done.is_set() and f.exists():
            obj=json.loads(f.read_text())
            if self.next==obj['completed_steps']:
                # Freeze final transfer timings once, so a lost final ACK/restart
                # resends exactly the same completion receipt.
                transfer_finish=self.out/'TRANSFER_FINISH.json'
                if transfer_finish.exists():payload=transfer_finish.read_bytes()
                else:
                    if set(self.ack_timings)!=set(range(self.next)):raise ValueError('incomplete transfer timing receipt')
                    obj['transfer_timings']={str(k):self.ack_timings[k] for k in range(self.next)}
                    payload=canonical(obj);atomic(transfer_finish,payload)
                a=self.send(self.config,'/finish',payload)
                if not a.get('durable') or a.get('completed_steps')!=self.next:raise ValueError('bad finish ACK')
                self.finish_sent=True
        return False
    def run(self):
        while not self.stop.is_set() and not self.finish_sent:
            try:
                self.wake.clear()
                if not self.attempt() and not self.finish_sent and not self.stop.is_set():self.wake.wait()
            except urllib.error.HTTPError as exc:
                self.error=str(exc)
                if 400<=exc.code<500:self.fatal=True;break
                self.stop.wait(.5)
            except ValueError as exc:self.error=str(exc);self.fatal=True;break
            except Exception as exc:self.error=repr(exc);self.stop.wait(.5)
        atomic(self.out/'TRANSFER.json',canonical(dict(acked=self.next,finish_sent=self.finish_sent,fatal=self.fatal,error=self.error,
              neural_commands=0,pending_records_retained=True)))
    def close(self,seconds=60):
        self.done.set();self.wake.set();self.thread.join(seconds)
        if self.thread.is_alive():self.stop.set();self.wake.set();self.thread.join(5)
        if self.thread.is_alive():raise RuntimeError('upload thread still active; preserve directory')

