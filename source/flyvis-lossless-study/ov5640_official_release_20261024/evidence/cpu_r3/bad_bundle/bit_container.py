import struct
def bit_header(raw):
    # Independent parser of the standard tagged .bit container; no bitstream
    # execution. See PYNQ2.7 embedded_device.parse_bit_header for the format.
    if len(raw)<32:raise ValueError('Truncated bitstream')
    size=struct.unpack_from('>H',raw)[0];pos=2+size
    if size!=9 or raw[2:pos]!=bytes.fromhex('0ff00ff00ff00ff000') or raw[pos:pos+2]!=b'\0\1':raise ValueError('BIT preamble')
    pos+=2;out={}
    for tag,name in ((97,'design'),(98,'part'),(99,'date'),(100,'time'),(101,'payload_bytes')):
        if pos>=len(raw) or raw[pos]!=tag:raise ValueError('BIT tag/order')
        pos+=1;width=4 if tag==101 else 2
        if pos+width>len(raw):raise ValueError('BIT length field')
        length=int.from_bytes(raw[pos:pos+width],'big');pos+=width
        if length<1 or pos+length>len(raw):raise ValueError('BIT field bounds')
        if tag==101:
            if pos+length!=len(raw) or b'\xaa\x99\x55\x66' not in raw[pos:pos+128]:raise ValueError('BIT payload/sync')
            out[name]=length
        else:
            if raw[pos+length-1]!=0:raise ValueError('BIT unterminated text')
            out[name]=raw[pos:pos+length-1].decode('ascii')
        pos+=length
    return out

