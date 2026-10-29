import http.client, json, uuid
from .control2 import require, sign, verified, BIT_SHA, HWH_SHA

class BoardClient:
    def init__(self, host, port, config):
        self.host, self.port, self.config = host, port, config
        self.ready_id = None
        self.active_connection = None

    def request(self, path, body=None):
        nonce = uuid.uuid4().hex
        if body is None:
            path += '?nonce=' + nonce
            raw = None
        else:
            body = dict(body, nonce=nonce, run_id=self.config['run_id'],
                        server_session=self.config['server_session'],
                        ready_id=self.ready_id, plan_sha256=self.config['plan_sha256'])
            raw = json.dumps(sign(body, self.config['control_key'])).encode('utf-8')
        connection = http.client.HTTPConnection(self.host, self.port, timeout=30 if path == '/evidence_begin' else 5)
        self.active_connection = connection
        try:
            connection.request('GET' if body is None else 'POST', path, body=raw,
                               headers={'Content-Type': 'application/json'})
            response = connection.getresponse()
            data = response.read(12 * 1024 * 1024 + 1)
            require(len(data) <= 12 * 1024 * 1024, 'BOARD_CONTROL_RESPONSE_SIZE')
            result = verified(json.loads(data), self.config['control_key'])
            require(response.status == 200, 'BOARD_CONTROL_REJECTED_' + str(result.get('error')))
            require(result.get('nonce') == nonce, 'BOARD_STALE_RESPONSE')
            for key in ('run_id', 'server_session', 'plan_sha256'):
                require(result.get(key) == self.config[key], 'BOARD_IDENTITY_' + key)
            require(result.get('bit_sha256') == BIT_SHA and result.get('hwh_sha256') == HWH_SHA,
                    'BOARD_IMAGE_IDENTITY')
            if self.ready_id is None:
                self.ready_id = result['ready_id']
            require(result['ready_id'] == self.ready_id, 'BOARD_SERVICE_RESTARTED')
            return result
        finally:
            connection.close()
            self.active_connection = None

