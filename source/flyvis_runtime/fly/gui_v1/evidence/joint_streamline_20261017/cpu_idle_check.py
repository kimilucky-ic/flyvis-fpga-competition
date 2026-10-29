"""One real loopback keepalive idle check; synthetic CPU identity, no devices."""
import json,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(OUT.parents[1]))
from test_joint_streamline import ClockTests

client,authority,_,_,diagnostics=ClockTests().fixture()
authority.declaration=dict(pc_authority_endpoint=dict(host='127.0.0.1',port=0))
authority.server=authority.thread=None
try:
    authority.start()
    client.handoff['pc_authority_endpoint']=dict(host='127.0.0.1',port=authority.server.server_address[1])
    client.check();connection=client.connection;fd=connection.sock.fileno()
    time.sleep(3.2)  # Exceeds the old server's 3s post-response idle timeout.
    client.check()
    assert client.connection is connection and client.connection.sock.fileno()==fd
    connects=sum(r['name']=='clock.connect' for r in diagnostics.rows)
    assert connects==1 and len(authority.seen)==2
    result=dict(status='PASS_CPU_LOOPBACK_KEEPALIVE_IDLE',idle_s=3.2,connects=connects,
        signed_checks=2,automatic_reconnection=False,neural_steps=0,board_connections=0)
    (OUT/'cpu_idle_check.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result),flush=True)
finally:client.close();authority.close()
