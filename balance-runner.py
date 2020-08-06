#!/usr/bin/env python3

import json
from collections import defaultdict
# XXX IOBTree

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
BURNERS = set([
    ZERO_ADDRESS,
    "0xfcba3e75865d2d561be8d220616520c171f12851",  # SUSD deposit
    "0xdcb6a51ea3ca5d3fd898fd6564757c7aaec3ca92",  # SUSD staking
])


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
            if el['to'] not in BURNERS:
                self.lps.add(el['to'])
            if el['from'] not in BURNERS:
                self.lps.add(el['from'])
            self.raw_transfers[el['address']].append(el)

        for el in virtual_prices:
            el['timestamp'] = int(el['timestamp'])
            el['block'] = int(el['block'])
            el['virtualPrice'] = int(el['virtualPrice'])
            self.raw_prices[el['address']].append(el)

        for a in self.raw_transfers.keys():
            self.raw_transfers[a] = sorted(
                    self.raw_transfers[a],
                    key=lambda el: (el['block'], el['from'] not in BURNERS, el['to'] in BURNERS))
        for a in self.raw_prices.keys():
            self.raw_prices[a] = sorted(self.raw_prices[a], key=lambda el: el['block'])

    def fill(self):
        for pool in self.raw_transfers.keys():
            for el in self.raw_transfers[pool]:
                if el['from'] not in BURNERS:
                    if len(self.balances[pool][el['from']]) > 0:
                        _, value = self.balances[pool][el['from']][-1]
                    else:
                        print(el)
                    value -= el['value']
                    self.balances[pool][el['from']].append((el['timestamp'], value))
                if el['to'] not in BURNERS:
                    if len(self.balances[pool][el['to']]) > 0:
                        _, value = self.balances[pool][el['to']][-1]
                    else:
                        value = 0
                    value += el['value']
                    self.balances[pool][el['to']].append((el['timestamp'], value))

    # Filling integrals:
    # * iterate time
    # * get vprice for each time (btree)
    # * get balance for each address at each time (btree)
    # * calc total*vp across all pools, fractions
    # * add vp * balance * dt to running integral for each address
    # * add vp * total to total integral

    # For balancer pools:
    # * have mappings deposit address -> BPT token
    # * calc bpt total, bpt fractions
    # * add vp * fraction * dt * bpt_fraction to integrals of addresses


if __name__ == '__main__':
    balances = Balances()
    balances.load('json/CRV_susdv2_sample.json')
    balances.fill()
    # XXX graph doesn't work with multiple Transfer events in the same tx
    # XXX needs fixing
    import IPython
    IPython.embed()
