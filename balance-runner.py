#!/usr/bin/env python3

import json
from collections import defaultdict
# XXX IOBTree

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class Balances:
    def __init__(self):
        self.balances = defaultdict(lambda: defaultdict(list))  # pool -> address -> [(timestamp, value, nonce?)]
        self.raw_transfers = defaultdict(list)
        self.raw_prices = defaultdict(list)
        self.lps = set()

    def load(self, fname):
        with open(fname) as f:
            data = json.load(f)

        transfers = data['data']['transfers']
        virtual_prices = data['data']['virtualPrices']
        for el in transfers:
            el['timestamp'] = int(el['timestamp'])
            el['value'] = int(el['value'])
            el['block'] = int(el['block'])
            if el['to'] != ZERO_ADDRESS:
                self.lps.add(el['to'])
            if el['from'] != ZERO_ADDRESS:
                self.lps.add(el['from'])
            self.raw_transfers['address'].append(el)

        for el in virtual_prices:
            el['timestamp'] = int(el['timestamp'])
            el['block'] = int(el['block'])
            el['virtualPrice'] = int(el['virtualPrice'])
            self.raw_prices['address'].append(el)

        for a in self.raw_transfers.keys():
            self.raw_transfers[a] = sorted(
                    self.raw_transfers[a],
                    key=lambda el: (el['block'], el['from'] != ZERO_ADDRESS, el['to'] == ZERO_ADDRESS))
        for a in self.raw_prices.keys():
            self.raw_prices[a] = sorted(self.raw_prices[a], key=lambda el: el['block'])

    def fill(self):
        for pool in self.raw_transfers.keys():
            for el in self.raw_transfers[pool]:
                pass


if __name__ == '__main__':
    balances = Balances()
    balances.load('json/CRV_susdv2_sample.json')
    balances.fill()
    import IPython
    IPython.embed()
