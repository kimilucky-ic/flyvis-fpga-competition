"""Narrow registration for migrated cam_iic; no transaction methods changed.
Register before Overlay construction. Original PYNQ2.7 iic.py/libiic.so remain.
CPU ABI tests do not attest native ARM library behavior or physical SCCB.
"""
def register_official_iic21(AxiIIC):
    if AxiIIC.bindto != ['xilinx.com:ip:axi_iic:2.0']:
        raise ValueError('Unexpected vendor driver registration; review version')
    class OfficialAxiIIC21(AxiIIC):
        bindto = ['xilinx.com:ip:axi_iic:2.1']
    return OfficialAxiIIC21
