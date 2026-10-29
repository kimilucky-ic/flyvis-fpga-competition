from pathlib import Path
p=Path('flyvis-lossless-study/ov5640_live_v261_20261026/pc/live_server.py');s=p.read_text();s=s.replace('import argparse,hmac,','import argparse,subprocess,hmac,',1)
s=s.replace('self.audit_result=None;self.audit_running=False;self.audit_lock=threading.Lock()','self.audit_result=None;self.audit_running=False;self.audit_lock=threading.Lock();self.audit_progress={}',1)
a=s.index('    def audit_if_ready(self):');b=s.index('    def status(self):',a)
s=s[:a]+'''    def audit_if_ready(self):
        with self.audit_lock:
            if self.audit_running or self.audit_result or not self.store.meta:return
            existing=self.store.path/'audit/RESULT.json'
            if existing.exists():self.audit_result=json.loads(existing.read_text());return
            if len(self.store.meta)<3 and self.store.final is None:return
            self.audit_running=True
            def work():
                try:
                    dest=self.store.path/'audit'
                    if dest.exists():dest=self.store.path/('audit_resume_'+str(time.time_ns()))
                    # Process setup, oracle, parsing and audit files never run in ACK handler.
                    job=self.store.path/'AUDIT_JOB.json';atomic(job,canonical(self.config))
                    cmd=[sys.executable,'-B',str(P/'pc/stream_audit.py'),'--records',str(self.store.path),'--config',str(job),'--bundle',str(P/'bundle'),'--output',str(dest),'--parent',str(os.getpid())]
                    with (self.store.path/('audit_process_'+str(time.time_ns())+'.log')).open('wb') as log:
                        child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0))
                        while child.poll() is None:
                            progress=self.store.path/'AUDIT_PROGRESS.json'
                            if progress.exists():self.audit_progress=json.loads(progress.read_text())
                            time.sleep(.25)
                        if child.returncode:raise RuntimeError('PC audit process stopped; retained output '+str(dest))
                    self.audit_result=json.loads((dest/'RESULT.json').read_text())
                    if dest.name!='audit':atomic(existing,canonical(self.audit_result))
                except Exception as exc:
                    self.audit_result=dict(status='AUDIT_ERROR',error=repr(exc));atomic(self.store.path/'AUDIT_ERROR.json',canonical(self.audit_result))
                finally:self.audit_running=False
            threading.Thread(target=work,name='line11-audit-monitor',daemon=True).start()
''' +s[b:]
s=s.replace("audit_status=self.audit_result['status'] if self.audit_result else ('AUDITING' if self.audit_running else 'PENDING'),","audit_status=self.audit_result['status'] if self.audit_result else ('AUDITING' if self.audit_running else 'PENDING'),\n                        audited_steps=self.audit_result.get('steps',0) if self.audit_result else self.audit_progress.get('steps',0),audit_schedule=self.audit_progress.get('status','PENDING'),")
s=s.replace("else:result=app.store.finish(json.loads(data));app.audit_if_ready()\n                self.reply(200,result)","else:result=app.store.finish(json.loads(data))\n                self.reply(200,result)\n                if route in ('/ingest','/finish'):app.audit_if_ready()")
p.write_text(s,encoding='utf-8')
