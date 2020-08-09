#!/usr/bin/env python3

import json
import datetime
from pprint import pprint
from collections import defaultdict
from scipy.interpolate import interp1d
from BTrees.OOBTree import OOBTree

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
REWARDS = [
    "0xdcb6a51ea3ca5d3fd898fd6564757c7aaec3ca92",   # susdv2
    "0x13c1542a468319688b89e323fe9a3be3a90ebb27",   # sbtc
    "0x13b54e8271b3e45ce71d8f4fc73ea936873a34fc",   # susd (old)
    "0x0001fb050fe7312791bf6475b96569d83f695c9f",   # YFI
    "0xb81d3cb2708530ea990a287142b82d058725c092",   # YFII
    "0x95284d906ab7f1bd86f522078973771ecbb20662",   # YFFI
    "0xd5bf26cdbd0b06d3fb0c6acd73db49d21b69e34f",   # YFID
    "0x9d03A0447aa49Ab26d0229914740c18161b08386",   # simp
    "0x803687e7756aff995d3053f7ce6cc41018ef62c3",   # brr.apy.finance
    "0xe4ffd96b5e6d2b6cdb91030c48cc932756c951b5",   # YYFI
    "0x35e3ad7652c7d5798412fea629f3e768662470cd",   # xearn/black wifey
]
REWARDS = [b.lower() for b in REWARDS]
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
BTC_TOKENS = [
    '0x49849c98ae39fff122806c06791fa73784fb3675',  # ren
    '0x075b1bb99792c9e1041ba13afef80c91a1e70fb3'   # sbtc
]
BPT_TOKENS = [
    "0x95C4B6C7CfF608c0CA048df8b81a484aA377172B",
    "0x939Ff8E09f7006bcBaDa0c41D837a74f77597dE1",
    "0x66c03a9d8c7DF62A05f043cAA4e33629780eaf7a",
    "0x6C0dD4dDEBaC30137E512B83FC54ac802d4CCe87",
    "0xe24AdB0693eC10c5D65eC0C09D5E9410a70b9f7D",
    "0xfA3bc6DDef77dc737b11Ca7b11623F1Cc77262E9",
    "0x0d167D8CBBfC00FFa239640134d780A808E8FBa0",
    "0x82865098c6cEbcc51385077034AAe96cE6E024D4",
    "0x81D258af4f640021a73ceA2A45849D4DfB3222eC",
    "0xc855F1572c8128ADd6F0503084Ba23930B7461f8",
    "0xDFb0CE371d4858d2ea247c1d2e07b40daF4e9298",
    "0x8194EFab90A290b987616F687Bc380b041A2Cc25",
    "0xC4B2c51F405E4E8bc498385240f6FEC11969D071",
    "0xD184C354AaAa92C84D5a1923b6Bca21D78a481da",
    "0x46e75e1a791b111d13c8dc38aba706a635f1e7f4",
    "0x9730dc8327807903844a71624f3b831c20bc6dda",
    "0xc4031959c45597051f4ac7b166673b144f811034",
    "0x125452a1f4adafa754453cae635fdc0bcaf21191",
    "0x87469cf4ea19822f2983751c1398f3fbbfbb63d2",
    "0x198059d85defcd671cc1ee1919979a934bc039be",
]
BPT_TOKENS = [t.lower() for t in BPT_TOKENS]
BPT_REWARDS = [
    "0x3a22df48d84957f907e67f4313e3d43179040d6e",
    "0xba86d69e8925382a4b915104148f8ab6f778e394",
    "0x7c8c77933e2fd6adc2ebfab5dc529c6787c57c34",
    "0xe247e535a8175dfb252fd691c5b2eda354620f70",
    "0x01877a9b00ae3c7101525721464f3e5840e07f49",
    "0x76f39a98ed09bf4fa4689741ef51724d9878023d",
    "0x4a5ee92022a9ff241a547cbc4986f5284bf628b2",
]
BPT_REWARDS = [t.lower() for t in BPT_REWARDS]

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

TIMESTEP = 24 * 3600


class Balances:
    def __init__(self, pool_tokens=POOL_TOKENS):
        self.balances = defaultdict(lambda: defaultdict(OOBTree))  # pool -> address -> [(timestamp, block, logIndex) -> value]
        self.raw_transfers = defaultdict(list)
        self.raw_prices = defaultdict(list)
        self.lps = set()
        self.price_splines = {}
        self.min_timestamp = int(datetime.datetime(2020, 1, 11).timestamp())  # before this date is really premine
        self.max_timestamp = 0
        self.user_integrals = defaultdict(list)  # user -> (timestamp, integral)
        self.total = 0.0
        self.pool_tokens = pool_tokens

    def load(self, tx_file, vp_file, btc_price_file):
        with open(tx_file) as f:
            data = json.load(f)

        with open(vp_file) as f:
            virtual_prices = json.load(f)

        with open(btc_price_file) as f:
            btc_prices = json.load(f)['prices']
        btc_prices = [(t // 1000, p) for t, p in btc_prices]
        t, btc_prices = list(zip(*btc_prices))
        self.btc_spline = interp1d(t, btc_prices, kind='linear', fill_value=(btc_prices[0], btc_prices[-1]), bounds_error=False)

        transfers = data
        for el in transfers:
            el['timestamp'] = int(el['timestamp'])
            el['block'] = int(el['block'])
            for event in el['transfers']:
                event['value'] = int(event['value'])
                event['logIndex'] = int(event['logIndex'])
                if event['to'] not in (REWARDS + [ZERO_ADDRESS]):  # != ZERO_ADDRESS:
                    self.lps.add(event['to'])
                if event['from'] not in (REWARDS + [ZERO_ADDRESS]):  # != ZERO_ADDRESS:
                    self.lps.add(event['from'])
                event['timestamp'] = el['timestamp']
                # self.min_timestamp = min(self.min_timestamp, event['timestamp'])
                self.max_timestamp = max(self.max_timestamp, event['timestamp'])
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
        for pool in self.pool_tokens:
            ts = [el['timestamp'] for el in self.raw_prices[pool]]
            vp = [el['virtualPrice'] for el in self.raw_prices[pool]]
            self.price_splines[pool] = interp1d(ts, vp, kind='linear', fill_value=(min(vp), max(vp)), bounds_error=False)

        for pool in self.pool_tokens:  # self.raw_transfers.keys():
            for el in self.raw_transfers[pool]:
                if el['from'] != el['to']:
                    key = (-el['timestamp'], -el['block'], -el['logIndex'])
                    if (el['from'] not in REWARDS + [ZERO_ADDRESS]) and (el['to'] not in REWARDS):  # != ZERO_ADDRESS:
                        tree = self.balances[pool][el['from']]
                        if key not in tree:
                            value = 0
                            if len(tree) > 0:
                                value = tree.values()[0]
                            elif el['value'] > 0:
                                pprint(el)
                            value -= el['value']
                            tree[key] = value
                    if (el['to'] not in REWARDS + [ZERO_ADDRESS]) and (el['from'] not in REWARDS):  # != ZERO_ADDRESS:
                        tree = self.balances[pool][el['to']]
                        if key not in tree:
                            value = 0
                            if len(tree) > 0:
                                value = tree.values()[0]
                            else:
                                value = 0
                            value += el['value']
                            tree[key] = value

        self.lps = list(self.lps)

    def get_balance(self, pool, addr, timestamp):
        pool = pool.lower()
        addr = addr.lower()
        tree = self.balances[pool][addr]
        try:
            return tree.values((-timestamp,))[0]
        except IndexError:
            return 0

    def fill_integrals(self):
        for t in range(self.min_timestamp, self.max_timestamp, TIMESTEP):
            total = 0
            deposits = defaultdict(int)
            for pool in self.pool_tokens:
                vp = float(self.price_splines[pool](t))
                if pool in BTC_TOKENS:
                    vp *= float(self.btc_spline(t))
                for addr in self.lps:
                    value = int(vp * self.get_balance(pool, addr, t))
                    total += value
                    deposits[addr] += value

            rel = {addr: value / total if total else 0 for addr, value in deposits.items()}
            for addr in self.lps:
                if len(self.user_integrals[addr]) == 0:
                    integral = 0
                else:
                    integral = self.user_integrals[addr][-1][1]
                integral += rel[addr]
                self.user_integrals[addr].append((t, integral))

            print(datetime.datetime.fromtimestamp(t), total / 1e18)
            self.total += 1.0

    def export(self, fname='output.json'):
        user_fractions = {}
        for addr in self.user_integrals:
            _, integral = self.user_integrals[addr][-1]
            user_fractions[addr] = integral / self.total
        with open(fname, 'w') as f:
            json.dump(user_fractions, f)
        self.user_fractions = user_fractions
        return user_fractions


class BPT:
    def __init__(self, balances_obj):
        self.balances = defaultdict(lambda: defaultdict(OOBTree))  # pool -> address -> [(timestamp, block, logIndex) -> value]
        self.raw_transfers = defaultdict(list)
        self.lps = set()
        self.min_timestamp = 1e12  # BPT pools appeared late
        self.max_timestamp = 0
        self.user_integrals = defaultdict(list)  # user -> (timestamp, integral)
        self.total = 0.0
        self.pool_tokens = BPT_TOKENS
        self.bcalc = balances_obj

    def load(self, tx_file):
        with open(tx_file) as f:
            data = json.load(f)

        transfers = data
        for el in transfers:
            el['timestamp'] = int(el['timestamp'])
            el['block'] = int(el['block'])
            for event in el['transfers']:
                event['value'] = int(event['value'])
                event['logIndex'] = int(event['logIndex'])
                if event['to'] not in (BPT_REWARDS + [ZERO_ADDRESS]):  # != ZERO_ADDRESS:
                    self.lps.add(event['to'])
                if event['from'] not in (BPT_REWARDS + [ZERO_ADDRESS]):  # != ZERO_ADDRESS:
                    self.lps.add(event['from'])
                event['timestamp'] = el['timestamp']
                self.min_timestamp = min(self.min_timestamp, event['timestamp'])
                self.max_timestamp = max(self.max_timestamp, event['timestamp'])
                event['block'] = el['block']
                self.raw_transfers[event['address']].append(event)

        for a in self.raw_transfers.keys():
            self.raw_transfers[a] = sorted(
                    self.raw_transfers[a],
                    key=lambda el: (el['block'], el['logIndex']))

    def fill(self):
        for pool in self.pool_tokens:  # self.raw_transfers.keys():
            for el in self.raw_transfers[pool]:
                key = (-el['timestamp'], -el['block'], -el['logIndex'])
                if (el['from'] not in BPT_REWARDS + [ZERO_ADDRESS]) and (el['to'] not in BPT_REWARDS):
                    tree = self.balances[pool][el['from']]
                    if key not in tree:
                        value = 0
                        if len(tree) > 0:
                            value = tree.values()[0]
                        elif el['value'] > 0:
                            pprint(el)
                        value -= el['value']
                        tree[key] = value
                if (el['to'] not in BPT_REWARDS + [ZERO_ADDRESS]) and (el['from'] not in BPT_REWARDS):
                    tree = self.balances[pool][el['to']]
                    if key not in tree:
                        value = 0
                        if len(tree) > 0:
                            value = tree.values()[0]
                        else:
                            value = 0
                        value += el['value']
                        tree[key] = value

        self.lps = list(self.lps)

    def get_balance(self, pool, addr, timestamp):
        pool = pool.lower()
        addr = addr.lower()
        tree = self.balances[pool][addr]
        try:
            return tree.values((-timestamp,))[0]
        except IndexError:
            return 0

    def fill_integrals(self):
        user_fractions = self.bcalc.user_fractions
        self.user_fractions = defaultdict(float)
        for pool in self.pool_tokens:
            bpt_total = 0
            bpt_integrals = defaultdict(list)
            for t in range(self.min_timestamp, self.max_timestamp, TIMESTEP):
                total = 0
                deposits = defaultdict(int)
                for addr in self.lps:
                    value = int(self.get_balance(pool, addr, t))
                    total += value
                    deposits[addr] += value

                rel = {addr: value / total if total else 0 for addr, value in deposits.items()}
                for addr in self.lps:
                    if len(bpt_integrals[addr]) == 0:
                        integral = 0
                    else:
                        integral = bpt_integrals[addr][-1][1]
                    integral += rel[addr]
                    bpt_integrals[addr].append((t, integral))

                bpt_total += sum(rel.values())  # only when there are some

            for addr in bpt_integrals:
                if bpt_total > 0:
                    self.user_fractions[addr] += bpt_integrals[addr][-1][1] / bpt_total * user_fractions[pool]
                else:
                    self.user_fractions[addr] += 0.0


    # For balancer pools:
    # * have mappings deposit address -> BPT token
    # * calc bpt total, bpt fractions
    # * add vp * fraction * dt * bpt_fraction to integrals of addresses


if __name__ == '__main__':
    balances = Balances()
    balances.load('json/transfer_events.json', 'json/virtual_prices.json', 'json/btc-prices.json')
    balances.fill()
    balances.fill_integrals()
    user_fractions = balances.export()
    bpt_obj = BPT(balances)
    bpt_obj.load('json/transferEventsBPT.json')
    bpt_obj.fill()
    bpt_obj.fill_integrals()
    for addr in BPT_TOKENS:
        user_fractions[addr] = 0
    for addr, val in bpt_obj.user_fractions.items():
        if addr not in user_fractions:
            user_fractions[addr] = 0
        user_fractions[addr] += val
    with open('output-with-bpt.json', 'w') as f:
        json.dump(user_fractions, f)
    print(min(user_fractions.values()))
    print(max(user_fractions.values()))
    print(sum(user_fractions.values()))
