import requests
import json
import hashlib
import hmac
import time


class BitfinexClient(object):

    BASE_URL = "https://api.bitfinex.com/"
    KEY = "U9eN4hYw5Xui3F2jDcHkpatbDzmInlOmd7dqWy6p6lx"
    SECRET = "reDJX0nBNWOpPo8zrza16FboAPlTq36asyeyjmL3hMh"

    def _nonce(self):

        return str(int(round(time.time() * 1000)))

    def _headers(self, path, nonce, body):

        signature = "/api/" + path + nonce + body
        h = hmac.new(self.SECRET.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
        signature = h.hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.KEY,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def active_orders(self):

        nonce = self._nonce()
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/orders"

        headers = self._headers(path, nonce, rawBody)

        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)

        if r.status_code == 200:

            return r.json()

        else:
            print (r.status_code)
            print (r)
            return ''

file = open('bf_orders.json', 'w')

json.dump(BitfinexClient().active_orders(), file)
