import json
import warnings
import os

import requests
from brownie import Contract, accounts, chain, network, config
from brownie.convert import to_address


config['autofetch_sources'] = True

warnings.filterwarnings("ignore")

APIKEY_ETHPLORER = os.getenv('APIKEY_ETHPLORER')
IPFS_PROJECT_ID = os.getenv('IPFS_PROJECT_ID')
IPFS_PROJECT_SECRET = os.getenv('IPFS_PROJECT_SECRET')


# this script is used to prepare, simulate and broadcast votes within Curve's DAO
# modify the constants below according the the comments, and then use `simulate` in
# a forked mainnet to verify the result of the vote prior to broadcasting on mainnet

# addresses related to the DAO - these should not need modification
CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6c65c637785e8f8b742ae6b0b9968",
    "voting": "0xe478de485ad2fe566d49342cbd03e49ed7db3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

CURVE_DAO_PARAM = {
    "agent": "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    "voting": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xf409Ce40B5bb1e4Ef8e97b1979629859c6d5481f",
    "agent": "0x00669DF67E4827FCc0E48A1838a8d5AB79281909",
    "voting": "0x1115c9b3168563354137cdc60efb66552dd50678",
    "token": "0x4c0947B16FB1f755A2D32EC21A0c4181f711C500",
    "quorum": 51,
}

# the intended target of the vote, should be one of the above constant dicts
TARGET = CURVE_DAO_OWNERSHIP

# address to create the vote from - you will need to modify this prior to mainnet use
SENDER = accounts[0]

# a list of calls to perform in the vote, formatted as a lsit of tuples
# in the format (target, function name, *input args).
#
# for example, to call:
# GaugeController("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB").add_gauge("0xFA712...", 0, 0)
#
# use the following:
# [("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB", "add_gauge", "0xFA712...", 0, 0),]
#
# commonly used addresses:
# GaugeController - 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
# GaugeProxy - 0x519AFB566c05E00cfB9af73496D00217A630e4D5
# PoolProxy - 0xeCb456EA5365865EbAb8a2661B0c503410e9B347


ACTIONS = [
    # token=tbtc "0x18084fbA666a33d37592fA2633fD49a74DD93a88",
    # A=100, fee=6 * 10**15, admin_fee=0,
    # price_oracle="0xbeF434E2aCF0FBaD1f0579d2376fED0d1CfC4217",
    # mpolicy="0xb8687d7dc9d8fa32fabde63E19b2dBC9bB8B2138",
    # loan_discount=9 * 10**16, liquidation_discount=6 * 10**16,
    # debt_ceiling=50 * 10**6 * 10**18
    ("0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC", "set_debt_ceiling",
     "0x8472a9a7632b173c8cf3a86d3afec50c35548e76", 0)
    # ("target", "fn_name", *args),
]

# description of the vote, will be pinned to IPFS
DESCRIPTION = "Set the old sfrxETH market debt ceiling to zero (new market is 50M)"


def prepare_evm_script():
    agent = Contract(TARGET["agent"])
    evm_script = "0x00000001"

    for address, fn_name, *args in ACTIONS:
        contract = Contract(address)
        fn = getattr(contract, fn_name)
        calldata = fn.encode_input(*args)
        agent_calldata = agent.execute.encode_input(address, 0, calldata)[2:]
        length = hex(len(agent_calldata) // 2)[2:].zfill(8)
        evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"

    return evm_script


def make_vote(sender=SENDER):
    if network.show_active() == 'mainnet':
        kw = {'from': sender, 'priority_fee': '1 gwei'}
    else:
        kw = {'from': sender}
    text = json.dumps({"text": DESCRIPTION})
    session = requests.Session()
    session.auth = (IPFS_PROJECT_ID, IPFS_PROJECT_SECRET)
    response = session.post("https://ipfs.infura.io:5001/api/v0/add", files={"file": text})
    ipfs_hash = response.json()["Hash"]
    print(f"ipfs hash: {ipfs_hash}")

    aragon = Contract(TARGET["voting"])
    evm_script = prepare_evm_script()
    if TARGET.get("forwarder"):
        # the emergency DAO only allows new votes via a forwarder contract
        # so we have to wrap the call in another layer of evm script
        vote_calldata = aragon.newVote.encode_input(evm_script, DESCRIPTION, False, False)[2:]
        length = hex(len(vote_calldata) // 2)[2:].zfill(8)
        evm_script = f"0x00000001{aragon.address[2:]}{length}{vote_calldata}"
        print(f"Target: {TARGET['forwarder']}\nEVM script: {evm_script}")
        tx = Contract(TARGET["forwarder"]).forward(evm_script, kw)
    else:
        print(f"Target: {aragon.address}\nEVM script: {evm_script}")
        tx = aragon.newVote(evm_script, f"ipfs:{ipfs_hash}", False, False, kw)

    vote_id = tx.events["StartVote"]["voteId"]

    print(f"\nSuccess! Vote ID: {vote_id}")
    return vote_id


def simulate():
    # fetch the top holders so we can pass the vote
    data = requests.get(
        f"https://api.ethplorer.io/getTopTokenHolders/{TARGET['token']}",
        params={"apiKey": "freekey", "limit": 100},
    ).json()["holders"]
    data = [{'address': '0x989AEb4d175e16225E39E87d0D97A3360524AD80', 'share': 49.}] + data
    data = data[::-1]

    # create a list of top holders that will be sufficient to make quorum
    holders = []
    weight = 0
    while weight < TARGET["quorum"] + 5:
        row = data.pop()
        holders.append(to_address(row["address"]))
        weight += row["share"]

    # make the new vote
    top_holder = holders[0]
    vote_id = make_vote(top_holder)

    # vote
    aragon = Contract(TARGET["voting"])
    for acct in holders:
        aragon.vote(vote_id, True, False, {"from": acct})

    # sleep for a week so it has time to pass
    chain.sleep(86400 * 7)

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, {"from": top_holder})
