from pathlib import Path
P=Path('flyvis-lossless-study/ov5640_live_v261_20261026')
p=P/'pc/live_server.py';s=p.read_text(encoding='utf-8-sig');s=s.replace('from round_sessions import Rounds,admission','from round_sessions import Rounds,admission\nimport fixed_entry')
s=s.replace('    initial_app=app\n','    initial_app=app\n    fixed_root=rounds.root if rounds else P\n    fixed_key=fixed_entry.prepare(fixed_root) if rounds else None\n',1)
a="                if route=='/hello':"
b="""                if route=='/runner':
                    if fixed_key is None or not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+fixed_key):return self.reply(403,{'error':'authorization'})
                    nonce=urllib.parse.parse_qs(u.query).get('nonce',[''])[0]
                    return self.reply(200,fixed_entry.response(rounds,fixed_key,nonce))
"""+a
assert s.count(a)==1;s=s.replace(a,b)
a="                if route=='/notebook':";b="""                if route=='/fixed-notebook' and fixed_key is not None:
                    return self.reply(200,(fixed_root/fixed_entry.NAME).read_bytes(),'application/x-ipynb+json')
"""+a
assert s.count(a)==1;s=s.replace(a,b);p.write_text(s,encoding='utf-8')
p=P/'assets/ui.js';s=p.read_text(encoding='utf-8-sig');s=s.replace("'LINE11_60S_'+s.session_id.slice(0,8)+'.ipynb'","'LINE11_START_60S.ipynb'");p.write_text(s,encoding='utf-8')
p=P/'assets/index.html';s=p.read_text(encoding='utf-8-sig');s=s.replace('href="/notebook"','href="/fixed-notebook"').replace('下载本轮Notebook','固定Notebook（首次下载）').replace('download="LINE11_OFFICIAL_LIVE_V261_60S.ipynb"','download="LINE11_START_60S.ipynb"')
a='先关闭上一轮已正常结束的Notebook内核，再将 <a href="/fixed-notebook" download="LINE11_START_60S.ipynb">单文件Notebook</a> 上传到板卡网页，以独立新内核运行。不要重新运行上一轮Notebook；每轮从初始神经状态开始。'
b='首次将 <a href="/fixed-notebook" download="LINE11_START_60S.ipynb">固定Notebook</a> 下载并上传到板卡，关闭之前已正常结束的旧Notebook内核。以后无需重新下载或上传：电脑点击“开始下一轮60秒”，板端在同一固定Notebook中选择“重启内核并运行全部”，再确认一次。仅上一轮正常关闭且验收通过后这样操作；异常保留内核。每轮从初始神经状态开始。'
assert a in s;s=s.replace(a,b);p.write_text(s,encoding='utf-8')
