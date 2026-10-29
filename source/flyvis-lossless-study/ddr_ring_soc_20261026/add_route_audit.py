from pathlib import Path
import shutil
p=Path(__file__).resolve().parent;b=Path('C:/fpga_work/line11_ring_20261026')
shutil.copy2(p/'audit_routed.tcl',b/'audit_routed.tcl')
f=b/'route.tcl';s=f.read_text();assert 'source audit_routed.tcl' not in s
s=s.replace('set f [open ROUTE_COMPLETED_REVIEW_REQUIRED.txt w]','source audit_routed.tcl\nset f [open ROUTE_COMPLETED_REVIEW_REQUIRED.txt w]');f.write_text(s)
print('Added routed ring ownership/clock structural checks')
