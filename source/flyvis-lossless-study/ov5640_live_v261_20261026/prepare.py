from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parent;O=R/'ov5640_live_crop_20261026';F=R/'vivado2026_1_20261026'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(P/'evidence').mkdir();(P/'tests').mkdir();(P/'pc').mkdir()
for root in [O,F]:
 ids=json.loads((root/'FINAL_MANIFEST_SHA256.json').read_text());assert all(sha(root/n)==h for n,h in ids.items())
 (P/'evidence'/('BASELINE_RELEASE_SHA256.json' if root==O else 'FIRMWARE_RELEASE_SHA256.json')).write_text(json.dumps(ids,indent=2))
for name in ['bundle','assets']:shutil.copytree(O/name,P/name,ignore=shutil.ignore_patterns('__pycache__'))
for f in (O/'pc').glob('*.py'):shutil.copy2(f,P/'pc'/f.name)
old='LINE11_OFFICIAL_LIVE_CROP_60S';new='LINE11_OFFICIAL_LIVE_V261_60S'
for name in ['bundle/live_board.py','bundle/offline_check.py','pc/live_server.py','assets/index.html']:
 f=P/name;s=f.read_text(encoding='utf-8-sig').replace(old,new).replace('运行铺满版60秒','运行2026.1铺满版60秒')
 if name=='assets/index.html':s=s.replace('中央裁剪60秒候选','2026.1中央裁剪60秒候选')
 f.write_text(s,encoding='utf-8')
info=json.loads((P/'bundle/release_info.json').read_text());fw=json.loads((F/'RESULT.json').read_text())
assert fw['status']=='PASS_VIVADO2026_1_FULL_SOC_100MHZ_BIT_HWH_OFFLINE_ONLY'
for key,filename in [('bit_sha256','flyvis_official.bit'),('hwh_sha256','flyvis_official.hwh')]:
 shutil.copy2(F/'release'/filename,P/'bundle'/filename)
 assert sha(P/'bundle'/filename)==fw[key]
 text=(P/'bundle/offline_check.py').read_text().replace(info[key],fw[key]);(P/'bundle/offline_check.py').write_text(text)
 info[key]=fw[key]
f=P/'bundle/offline_check.py';f.write_text(f.read_text().replace(info['source_routed_dcp_sha256'],fw['routed_dcp_sha256']))
info.update(revision=new,software_revision=new,tool=fw['tool'],source_candidate=F.name,source_routed_dcp_sha256=fw['routed_dcp_sha256'],fix='Vivado2026.1 rebuilt paired firmware; passed center-square mapping and runtime unchanged',physical_acceptance='PENDING_NEW_BITSTREAM_OPERATOR_RUN')
(P/'bundle/release_info.json').write_text(json.dumps(info,indent=2)+'\n')
s=(O/'build_release.py').read_text().replace(old,new).replace('8797','8798').replace('60_34f67624.cmd','2026.160_da27d917.cmd').replace('运行铺满版60秒','运行2026.1铺满版60秒')
s=s.replace('中央正方形铺满 · DDR循环60秒候选','2026.1固件 · 中央正方形铺满 · DDR循环60秒候选').replace('加载与已通过循环版相同的固件一次','加载本候选的2026.1新固件一次')
s=s.replace('本候选已有CPU/RTL和完整SoC布局布线证据，循环版本已完成实板60秒1070步全状态验收；本次裁剪映射仅完成CPU验证。板上首次运行仍需由操作者执行。','保留的旧固件铺满版已完成实板60秒1093步全状态验收。本候选采用Vivado2026.1重新生成的BIT/HWH，已通过完整SoC100MHz布局布线及文件配对检查；采集、输入映射、记录与验收逻辑沿用旧版。新固件的实板正确性与速度尚待本次操作者运行验证，旧版PASS不等于新版PASS。')
(P/'build_release.py').write_text(s,encoding='utf-8')
for n in ['test_release.py','test_http.py']:
 s=(O/'tests'/n).read_text().replace(old,new).replace('运行铺满版60秒','运行2026.1铺满版60秒').replace("P.parent/'ov5640_live_ring_20261026'","P.parent/'ov5640_live_crop_20261026'").replace('old_files_unchanged=87','old_files_unchanged=79').replace('PASS_CPU_LOCALHOST_CROP_NOTEBOOK_DELIVERY','PASS_CPU_LOCALHOST_V261_NOTEBOOK_DELIVERY')
 (P/'tests'/n).write_text(s,encoding='utf-8')
shutil.copy2(O/'60_34f67624.cmd',P/'2026.160_da27d917.cmd')
print('Prepared independent2026.1 crop package; no session records copied and no board actions')
