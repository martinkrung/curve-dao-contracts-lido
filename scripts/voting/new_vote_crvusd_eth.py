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
# SENDER = accounts[0]
SENDER = accounts.at("0x425d16B0e08a28A3Ff9e4404AE99D78C0a076C5A", force=True)  # accounts[0]

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
    # token=weth "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    # A=100, fee=6 * 10**15, admin_fee=0,
    # price_oracle="0x966cBDeceFB60A289b0460F7638f4A75F432cA06",
    # mpolicy="0x1E7d3bf98d3f8D8CE193236c3e0eC4b00e32DaaE",
    # loan_discount=9 * 10**16, liquidation_discount=6 * 10**16,
    # debt_ceiling=200 * 10**6 * 10**18
    ("0x966cBDeceFB60A289b0460F7638f4A75F432cA06", 'price_w'),
    ("0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC", "add_market",
     "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 100, 6 * 10**15, 0,
     "0x966cBDeceFB60A289b0460F7638f4A75F432cA06",
     "0x1E7d3bf98d3f8D8CE193236c3e0eC4b00e32DaaE",
     9 * 10**16, 6 * 10**16, 200 * 10**6 * 10**18)
    # ("target", "fn_name", *args),
]

# description of the vote, will be pinned to IPFS
DESCRIPTION = "Deploy WETH market with 200M crvUSD debt ceiling. Safety parameters are the same as for staked ETH markets, ETH price oracle at 0x966cBDeceFB60A289b0460F7638f4A75F432cA06"


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
    # Test with weth contract
    # print("Test with weth contract") 
    # test = Contract.from_explorer("0xe478de485ad2fe566d49342cbd03e49ed7db3356")


    # fetch the top holders so we can pass the vote
    data = requests.get(
        f"https://api.ethplorer.io/getTopTokenHolders/{TARGET['token']}",
        params={"apiKey": APIKEY_ETHPLORER, "limit": 100},
    ).json()["holders"]

    # https://api.ethplorer.io/getTopTokenHolders/0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2?apiKey=EK-4SrrN-3pwr7Uf-GuN1q&limit=100



    print (TARGET['token'])

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
    print(holders)
    for acct in holders:
        aragon.vote(356, True, False, {"from": acct})  # Controller impl vote
        aragon.vote(vote_id, True, False, {"from": acct})

    # sleep for a week so it has time to pass
    chain.sleep(86400 * 7)

    # New controller
    aragon.executeVote(356, {"from": top_holder})

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, {"from": top_holder})

    # Now let's borrow something
    # First, hack aave to do it
    aave = accounts.at("0x030bA81f1c18d280636F32af80b9AAd02Cf0854e", force=True)
    weth = Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    weth.transfer(top_holder, 100 * 10**18, {'from': aave})

    # Initiate new market objects
    factory = Contract("0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC")
    assert factory.n_collaterals() == 3
    sfrxeth_controller = Contract(factory.controllers(0))
    sfrxeth_amm = Contract(factory.amms(0))
    weth_controller = Contract.from_abi('Controller', factory.controllers(2), sfrxeth_controller.abi)
    weth_amm = Contract.from_abi('AMM', factory.amms(2), sfrxeth_amm.abi)
    crvusd = Contract('0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E')

    assert weth_amm.coins(0) == crvusd.address  # crvUSD
    assert weth_amm.coins(1) == weth.address
    assert weth_controller.amm() == weth_amm.address
    assert weth_controller.collateral_token() == weth.address

    print('wBTC price:', weth_amm.price_oracle() / 1e18)

    # Borrow and check crvUSD amount
    weth.approve(weth_controller, 2**256 - 1, {'from': top_holder})
    try:
        # Cannot borrow 10k
        weth_controller.create_loan(10**18, 10000 * 10**18, 4, {'from': top_holder})
    except Exception:
        pass
    else:
        raise Exception("Didn't raise")
    # But can 1k
    weth_controller.create_loan(10**18, 1000 * 10**18, 4, {'from': top_holder})
    assert crvusd.balanceOf(top_holder) == 1000 * 10**18

    weth_controller.borrow_more(0, 10**18, {'from': top_holder})
