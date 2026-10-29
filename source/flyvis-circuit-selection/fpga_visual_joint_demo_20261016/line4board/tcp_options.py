"""Option only; retain the exact original framing and sendall path."""
import socket
def configure(sock):
    sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
    value=sock.getsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY)
    if value!=1:raise RuntimeError('TCP_NODELAY_NOT_CONFIRMED_NO_RETRY')
    return dict(TCP_NODELAY=value,neural_wire_changed=False,automatic_retry=False)
