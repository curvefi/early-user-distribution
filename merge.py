import json

with open('json/transferEventsFinal.json', 'r') as f:
    transfer_events = json.load(f)

with open('json/transferEventsCompound1.json', 'r') as f:
    comp_events = json.load(f)

with open('json/transfer_events.json', 'w') as f:
    transfer_events += comp_events
    json.dump(transfer_events, f)

with open('json/transferEventsBPTFinal.json', 'r') as f:
    bpt_events = json.load(f)

with open('json/transferEventscrYCRVFinal.json', 'r') as f:
    cream_events = json.load(f)

with open('json/transfer_events_bpt.json', 'w') as f:
    bpt_events += cream_events
    json.dump(bpt_events, f)

with open('json/virtualPricesFinal.json', 'r') as f:
    vp = json.load(f)

with open('json/virtualPricesPAXFinal.json', 'r') as f:
    vpax = json.load(f)

with open('json/virtual_prices.json', 'w') as f:
    vp += vpax
    json.dump(vp, f)
