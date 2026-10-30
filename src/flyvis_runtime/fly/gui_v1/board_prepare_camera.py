# Fixed human-run preparation cell. Keep this cell for subsequent runs.
# Requires the existing camera3 service/bundle and original initialized handles.
# No code from the PC is executed before its current-parent HMAC is verified.
import urllib.request,json,hashlib,hmac
with urllib.request.urlopen('http://192.168.2.89:18790/operator-entry',timeout=5) as line2_reply:
    line2_packet=json.loads(line2_reply.read(200001))
line2_prior=camera3_service_instance.config
line2_body=line2_packet['body']
line2_mac=hmac.new(bytes.fromhex(line2_prior['control_key']),json.dumps(line2_body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
assert hmac.compare_digest(line2_mac,line2_packet['mac']),'PC preparation signature mismatch; stop'
assert line2_body['schema']=='flyvis-signed-human-prepare-entry/v1' and line2_body['prior_run_id']==line2_prior['run_id'] and line2_body['prior_scope_sha256']==line2_prior['scope_sha256'],'Prior service changed; stop'
assert hashlib.sha256(line2_body['source'].encode()).hexdigest()==line2_body['source_sha256'],'Preparation source changed; stop'
exec(compile(line2_body['source'],'LINE2_SIGNED_PREPARATION','exec'),globals(),globals())
