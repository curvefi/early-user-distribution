#!/usr/bin/env python3

import json
from pprint import pprint
from collections import defaultdict
from scipy.interpolate import interp1d
from BTrees.IOBTree import IOBTree

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
BURNERS = set([
    ZERO_ADDRESS,
    # "0xfcba3e75865d2d561be8d220616520c171f12851",  # SUSD deposit
    "0xdcb6a51ea3ca5d3fd898fd6564757c7aaec3ca92",  # SUSD staking
])
POOL_TOKENS = [
    '0xdbe281e17540da5305eb2aefb8cef70e6db1a0a9',  # compound1
    '0x3740fb63ab7a09891d7c0d4299442a551d06f5fd',  # compound2
    '0x845838df265dcd2c412a1dc9e959c7d08537f8a2',  # compound3
    '0x9fc689ccada600b6df723d9e47d84d76664a1f23',  # USDT
    '0xdf5e0e81dff6faf3a7e52ba697820c5e32d806a8',  # y
    '0x3b3ac5386837dc563660fb6a0937dfaa5924333b',  # busd
    '0x2b645a6a426f22fb7954dc15e583e3737b8d1434',  # susd (old, meta)
    '0xc25a3a3b969415c80451098fa907ec722572917f',  # susdv2
    '0xd905e2eaebe188fc92179b6350807d8bd91db0d8',  # pax
    '0x49849c98ae39fff122806c06791fa73784fb3675',  # ren
    '0x075b1bb99792c9e1041ba13afef80c91a1e70fb3'   # sbtc
]

POOL2TOKEN = {
    '0xe5fdbab9ad428bbb469dee4cb6608c0a8895cba5': '0xdbe281e17540da5305eb2aefb8cef70e6db1a0a9',  # compound1
    '0x2e60cf74d81ac34eb21eeff58db4d385920ef419': '0x3740fb63ab7a09891d7c0d4299442a551d06f5fd',  # compound2
    '0xa2b47e3d5c44877cca798226b7b8118f9bfb7a56': '0x845838df265dcd2c412a1dc9e959c7d08537f8a2',  # compound3
    '0x52ea46506b9cc5ef470c5bf89f17dc28bb35d85c': '0x9fc689ccada600b6df723d9e47d84d76664a1f23',  # USDT
    '0x45f783cce6b7ff23b2ab2d70e416cdb7d6055f51': '0xdf5e0e81dff6faf3a7e52ba697820c5e32d806a8',  # y
    '0x79a8c46dea5ada233abaffd40f3a0a2b1e5a4f27': '0x3b3ac5386837dc563660fb6a0937dfaa5924333b',  # busd
    '0xedf54bc005bc2df0cc6a675596e843d28b16a966': '0x2b645a6a426f22fb7954dc15e583e3737b8d1434',  # susd (old, meta)
    '0xa5407eae9ba41422680e2e00537571bcc53efbfd': '0xc25a3a3b969415c80451098fa907ec722572917f',  # susdv2
    '0x06364f10b501e868329afbc005b3492902d6c763': '0xd905e2eaebe188fc92179b6350807d8bd91db0d8',  # pax
    '0x93054188d876f558f4a66b2ef1d97d16edf0895b': '0x49849c98ae39fff122806c06791fa73784fb3675',  # ren
    '0x7fc77b5c7614e1533320ea6ddc2eb61fa00a9714': '0x075b1bb99792c9e1041ba13afef80c91a1e70fb3'   # sbtc
}


class Balances:
    def __init__(self):
        self.balances = defaultdict(lambda: defaultdict(list))  # pool -> address -> [(timestamp, value, nonce?)]
        self.raw_transfers = defaultdict(list)
        self.raw_prices = defaultdict(list)
        self.lps = set()
        self.price_splines = {}

    def load(self, tx_file, vp_file):
        with open(tx_file) as f:
            data = json.load(f)

        with open(vp_file) as f:
            virtual_prices = json.load(f)

        transfers = data
        for el in transfers:
            el['timestamp'] = int(el['timestamp'])
            el['block'] = int(el['block'])
            for event in el['transfers']:
                event['value'] = int(event['value'])
                event['logIndex'] = int(event['logIndex'])
                if event['to'] not in BURNERS:
                    self.lps.add(event['to'])
                if event['from'] not in BURNERS:
                    self.lps.add(event['from'])
                event['timestamp'] = el['timestamp']
                event['block'] = el['block']
                self.raw_transfers[event['address']].append(event)

        for el in virtual_prices:
            el['timestamp'] = int(el['timestamp'])
            el['block'] = int(el['block'])
            el['virtualPrice'] = int(el['virtualPrice']) / 1e18
            self.raw_prices[POOL2TOKEN[el['address']]].append(el)

        for a in self.raw_transfers.keys():
            self.raw_transfers[a] = sorted(
                    self.raw_transfers[a],
                    key=lambda el: (el['block'], el['logIndex']))
        for a in self.raw_prices.keys():
            self.raw_prices[a] = sorted(self.raw_prices[a], key=lambda el: el['block'])

    def fill(self):
        for pool in POOL_TOKENS:
            if pool != '0xd905e2eaebe188fc92179b6350807d8bd91db0d8':  # XXX no pax?
                print(pool)
                ts = [el['timestamp'] for el in self.raw_prices[pool]]
                vp = [el['virtualPrice'] for el in self.raw_prices[pool]]
                self.price_splines[pool] = interp1d(ts, vp, kind='linear', fill_value=(min(vp), max(vp)))
            else:
                self.price_splines[pool] = lambda x: 1.0  # XXX

        for pool in POOL_TOKENS:  # self.raw_transfers.keys():
            for el in self.raw_transfers[pool]:
                if el['from'] not in BURNERS:
                    if len(self.balances[pool][el['from']]) > 0:
                        _, value = self.balances[pool][el['from']][-1]
                    elif el['value'] > 0:
                        pprint(el)
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
    balances.load('json/transfer_events.json', 'json/virtualPrices.json')
    balances.fill()
    import IPython
    IPython.embed()
