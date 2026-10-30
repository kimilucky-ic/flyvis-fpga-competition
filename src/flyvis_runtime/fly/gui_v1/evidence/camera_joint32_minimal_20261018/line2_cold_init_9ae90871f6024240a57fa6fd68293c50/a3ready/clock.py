"""One authenticated PC-clock sample mapped to a conservative PS monotonic interval.

PC UTC defines the scope's time authority; this is NOT NTP/GPS attestation.
No cross-host monotonic timestamps are subtracted. No system clock is changed.
"""
import hashlib,json,secrets,threading,time
from datetime import datetime
from pathlib import Path
from .control2 import require,sign,verified

POLICY='PC_AUTHORITY_PS_MONOTONIC_INTERVAL/v1'
MAX_RTT_NS=10_000_000_000
MAX_SAMPLE_NS=20_000_000
MAX_AGE_NS=300_000_000_000
JUMP_NS=200_000_000
RATE_PPM=1000
KEYS=('run_id','server_session','boot_id','scope_sha256','plan_sha256','listener_id','start_utc','end_utc')
def boot_id():return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
def binding(c):return {k:c[k] for k in KEYS}
def utc_ns(value):
    d=datetime.fromisoformat(value);require(d.tzinfo is not None,'SCOPE_TIMEZONE_REQUIRED')
    return int(d.timestamp()*1_000_000_000)
def scope_bounds(c):
    a,b=utc_ns(c['start_utc']),utc_ns(c['end_utc']);require(0<b-a<=1800_000_000_000,'SCOPE_SPAN');return a,b

class PCClockAuthority:
    def init__(self,*,mono_ns=time.monotonic_ns,wall_ns=time.time_ns):
        self.mono,self.wall=mono_ns,wall_ns;self.id=secrets.token_hex(16)
        self.m0=self.last_m=self.mono();self.w0=self.wall();self.failed=False;self.answered=set()
    def check(self):
        require(not self.failed,'PC_CLOCK_QUARANTINED')
        try:
            m=self.mono();w=self.wall();require(m>=self.last_m and 0<=m-self.m0<=MAX_AGE_NS,'PC_MONOTONIC_REVERSED_OR_AUTHORITY_TOO_OLD')
            require(abs((w-self.w0)-(m-self.m0))<=JUMP_NS+(m-self.m0)*RATE_PPM//1_000_000,'PC_WALL_CLOCK_JUMP')
            self.last_m=m;return w
        except BaseException:self.failed=True;raise
    def answer(self,challenge,config):
        self.check();c=verified(challenge,config['control_key'])
        require(c.get('schema')=='flyvis-clock-challenge/v1' and c.get('binding')==binding(config),'PC_CLOCK_CHALLENGE_IDENTITY')
        nonce=c.get('nonce');require(isinstance(nonce,str) and len(nonce)==32 and nonce not in self.answered,'PC_CLOCK_CHALLENGE_REPLAY')
        self.answered.add(nonce)
        before=self.mono();wall=self.check();after=self.mono()
        require(0<=after-before<=MAX_SAMPLE_NS,'PC_CLOCK_SAMPLE_DELAY')
        begin,end=scope_bounds(config);require(begin<=wall<end,'PC_AUTHORITY_SCOPE_EXPIRED')
        return sign(dict(schema='flyvis-clock-proof/v1',policy=POLICY,binding=binding(config),nonce=nonce,
            pc_clock_id=self.id,pc_utc_ns=wall,pc_sample_uncertainty_ns=max(1000,after-before),
            max_relative_rate_error_ppm=RATE_PPM,pc_clock_jump_guard_ns=JUMP_NS),config['control_key'])

class BoardClockHandshake:
    def init__(self,config,*,mono_ns=time.monotonic_ns,wall_ns=time.time_ns,boot=boot_id):
        self.c=config;self.fixed=binding(config);scope_bounds(config)
        self.mono,self.wall,self.boot=mono_ns,wall_ns,boot
        require(self.boot()==config['boot_id'],'CLOCK_BOOT_CHANGED')
        self.m0=self.mono();self.w0=self.wall();self.nonce=secrets.token_hex(16);self.consumed=False;self.issued=False
    def challenge(self):
        require(not self.issued and not self.consumed,'CLOCK_CHALLENGE_CONSUMED');self.issued=True
        return sign(dict(schema='flyvis-clock-challenge/v1',binding=self.fixed,nonce=self.nonce),self.c['control_key'])
    def accept(self,packet):
        require(self.issued and not self.consumed,'CLOCK_PROOF_CONSUMED');self.consumed=True
        m=self.mono();wall=self.wall();rtt=m-self.m0
        require(binding(self.c)==self.fixed and self.boot()==self.c['boot_id'],'CLOCK_BOOT_OR_SCOPE_CHANGED')
        require(0<=rtt<=MAX_RTT_NS,'CLOCK_HANDSHAKE_DELAY_OR_REVERSE')
        require(abs((wall-self.w0)-rtt)<=JUMP_NS+rtt*RATE_PPM//1_000_000,'PS_WALL_CLOCK_JUMP_DURING_HANDSHAKE')
        p=verified(packet,self.c['control_key'])
        require(p.get('schema')=='flyvis-clock-proof/v1' and p.get('policy')==POLICY and p.get('binding')==self.fixed
                and p.get('nonce')==self.nonce,'CLOCK_PROOF_IDENTITY')
        require(p.get('max_relative_rate_error_ppm')==RATE_PPM and p.get('pc_clock_jump_guard_ns')==JUMP_NS,'CLOCK_PROOF_POLICY')
        u=p.get('pc_utc_ns');error=p.get('pc_sample_uncertainty_ns')
        require(type(u) is int and type(error) is int and 0<=error<=MAX_SAMPLE_NS,'CLOCK_PROOF_SAMPLE')
        require(isinstance(p.get('pc_clock_id'),str) and len(p['pc_clock_id'])==32,'CLOCK_AUTHORITY_ID')
        # Sample occurs somewhere between challenge creation and proof receipt.
        # The full measured RTT is kept as uncertainty; no symmetric-LAN claim.
        denominator=1_000_000-RATE_PPM
        rtt_upper=(rtt*1_000_000+denominator-1)//denominator
        # Budget a move between both extremes permitted by the PC clock guard.
        tolerance=2*JUMP_NS
        g=MonotonicScope(self.c,m,wall,u-error-tolerance,u+error+rtt_upper+tolerance,p,self.mono,self.wall,self.boot)
        g.check(self.c);return g

class MonotonicScope:
    def init__(self,c,m,wall,lower,upper,proof,mono,wall_fn,boot):
        self.fixed=binding(c);self.m0=self.last_m=m;self.w0=wall;self.lower0,self.upper0=lower,upper
        self.proof=proof;self.mono,self.wall,self.boot=mono,wall_fn,boot;self.lock=threading.RLock();self.failed=False
    def _bounds(self,c):
        require(not self.failed,'CLOCK_GUARD_QUARANTINED')
        require(binding(c)==self.fixed and self.boot()==c['boot_id'],'CLOCK_BOOT_OR_SCOPE_CHANGED')
        m=self.mono();age=m-self.m0;wall=self.wall()
        require(m>=self.last_m and 0<=age<=MAX_AGE_NS,'CLOCK_REVERSED_OR_PROOF_TOO_OLD')
        require(abs((wall-self.w0)-age)<=JUMP_NS+age*RATE_PPM//1_000_000,'PS_WALL_CLOCK_JUMP')
        self.last_m=m;drift=(age*RATE_PPM+999999)//1_000_000
        return self.lower0+age-drift,self.upper0+age+drift
    def check(self,c):
        with self.lock:
            try:
                low,high=self._bounds(c);begin,end=scope_bounds(c)
                require(begin<=low<=high<end,'AUTHORITY_INTERVAL_OUTSIDE_SCOPE')
                return dict(policy=POLICY,utc_lower_ns=low,utc_upper_ns=high,uncertainty_width_ns=high-low,
                    pc_clock_id=self.proof['pc_clock_id'],max_proof_age_ns=MAX_AGE_NS,rate_error_bound_ppm=RATE_PPM,PC_guard_tolerance_ns=2*JUMP_NS)
            except BaseException:self.failed=True;raise
    def remaining_s(self,c):
        upper=self.check(c)['utc_upper_ns'];return max(0,(scope_bounds(c)[1]-upper)/1e9/(1+RATE_PPM/1e6))
    def receipt(self,c):
        return dict(self.check(c),schema='flyvis-authoritative-time-receipt/v1',binding=self.fixed,
            proof=self.proof,proof_sha256=hashlib.sha256(json.dumps(self.proof,sort_keys=True).encode()).hexdigest(),
            ps_wall_role='JUMP_DETECTION_ONLY_NOT_SCOPE_AUTHORITY',absolute_UTC_accuracy='NOT_EXTERNALLY_ATTESTED')
