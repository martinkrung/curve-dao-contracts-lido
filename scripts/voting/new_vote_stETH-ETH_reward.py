import json
import warnings
import os

import requests
from brownie import Contract, accounts, chain, network, config
from brownie import StakingRewards, CurveLiquidityFarmingManager
from brownie.convert import to_address


config['autofetch_sources'] = True

warnings.filterwarnings("ignore")

VECRV_WHALE = os.getenv('VECRV_WHALE')
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


# wsteh
reward_token_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
# Lido: Rewards Committee Multisig 
distributor_address = "0x87D93d9B2C672bf9c9642d853a8682546a5012B5"

# old steth pool
gauge_old = "0x182B723a58739a9c974cFDB385ceaDb237453c28"
gauge_old_admin = "0x519AFB566c05E00cfB9af73496D00217A630e4D5"

# stETH ng
gauge_ng = "0x79F21BC30632cd40d2aF8134B469a0EB4C9574AA"
gauge_factory_ng = "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
gauge_factory_admin_ng = "0x742C3cF9Af45f91B109a81EfEaf11535ECDe9571"


# Optimism - Curve - wstETH-ETH:
# Pool: 0xb90b9b1f91a01ea22a182cd84c1e22222e39b415
# Multisig: 0x5033823F27c5f977707B58F0351adcD732C955Dd
# Reward Token: 0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb
# Gauge: 0xd53ccbfed6577d8dc82987e766e75e3cb73a8563

# Arbitrum - Curve - wstETH-ETH:
# Pool: 0x6eb2dc694eb516b16dc9fbc678c60052bbdd7d80
# Multisig: 0x8C2b8595eA1b627427EFE4f29A64b145DF439d16
# Reward Token: 0x5979D7b546E38E414F7E9822514be443A4800529
# Gauge: 0x098ef55011b6b8c99845128114a9d9159777d697 // https://arbiscan.io/address/0x098ef55011b6b8c99845128114a9d9159777d697
# Factory: 0xabc000d88f23bb45525e447528dbf656a9d55bf5 // https://arbiscan.io/address/0xabc000d88f23bb45525e447528dbf656a9d55bf5


## tricryptolama pool

## https://curve.fi/#/ethereum/pools/factory-tricrypto-2/deposit

# Pool 0x2889302a794da87fbf1d6db415c1492194663d13

gauge_tricryptolama = "0x60d3d7ebbc44dc810a743703184f062d00e6db7e"


def deployContractsOldPool():

    # msg.sender is set to owner
    # start with this, because we need curve_liquidity_farming_manager address from deployed StakingRewards



    CurveLiquidityFarmingManagerEwm = CurveLiquidityFarmingManager.deploy({'from': accounts[0]})


    owner = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c" # Lido agent
    curve_liquidity_farming_manager = CurveLiquidityFarmingManagerEwm # old one 0x753D5167C31fBEB5b49624314d74A957Eb27170
    reward_token_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0" # wsteth
    staking_token = "0x06325440D014e39736583c165C2963BA99fAf14E" # Curve.fi ETH/stETH (steCRV) Token 
    rewards_duration = 86400 * 1 # in Seconds? can be reset with setRewardsDuration()

    # old tx for LDO token as reference https://etherscan.io/tx/0x463cc85643784ec6eda246cff1366e8aa0ee964400485c2d5eee25f0e9044edc

    StakingRewardsEvm = StakingRewards.deploy(owner, curve_liquidity_farming_manager, reward_token_address, staking_token, rewards_duration, {'from': accounts[0]}, publish_source=False)
    try:
        StakingRewardsEvm.setRewardsDuration(86400*2)
    except:
        print(f"This error is expectd as only owner can call setRewardsDuration() ")

    print(f"StakingRewardsAddress: {StakingRewardsEvm}")

    
    # set rewards_contract to StakingRewards
    CurveLiquidityFarmingManagerEwm.set_rewards_contract(StakingRewardsEvm)
    # set ownership to Lido agent
    CurveLiquidityFarmingManagerEwm.transfer_ownership(owner)

    signature_old = "a694fc3a2e1a7d4d3d18b9120000000000000000000000000000000000000000"
    deposit_sig =  StakingRewardsEvm.stake.signature  
    withdraw_sig = StakingRewardsEvm.withdraw.signature
    claim_sig = StakingRewardsEvm.getReward.signature

    print(f"deposit_sig: {deposit_sig}")
    print(f"withdraw_sig: {withdraw_sig}")
    print(f"claim_sig: {claim_sig}")

    signature =  deposit_sig[2:] + withdraw_sig[2:] + claim_sig[2:] + "0000000000000000000000000000000000000000"

    print(f"signature_old: {signature_old}")

    print(f"signature: {signature}")

    empty = "0x0000000000000000000000000000000000000000"
    reward_tokens = [reward_token_address, empty, empty, empty, empty, empty, empty, empty]
    gauge_old = "0x182B723a58739a9c974cFDB385ceaDb237453c28"

    # gauge_old_evm = Contract(gauge_old)
    # gauge_old_evm.set_rewards(StakingRewardsEvm, signature, reward_tokens, {'from': gauge_old_admin}   )

    # gauge_old_admin_evm = Contract(gauge_old_admin)
    # gauge_old_admin_evm.set_rewards(gauge_old, StakingRewardsEvm, signature, reward_tokens, {'from': TARGET["agent"]})

    return(StakingRewardsEvm, signature, reward_tokens)


StakingRewardsEvm, signature, reward_tokens = deployContractsOldPool()

ACTIONS = [
    # token=tbtc "0x18084fbA666a33d37592fA2633fD49a74DD93a88",
    # A=100, fee=6 * 10**15, admin_fee=0,
    # price_oracle="0xbeF434E2aCF0FBaD1f0579d2376fED0d1CfC4217",
    # mpolicy="0xb8687d7dc9d8fa32fabde63E19b2dBC9bB8B2138",
    # loan_discount=9 * 10**16, liquidation_discount=6 * 10**16,
    # debt_ceiling=50 * 10**6 * 10**18
    (gauge_old_admin, "set_rewards",
     gauge_old, StakingRewardsEvm, signature, reward_tokens),
    (gauge_factory_admin_ng, "add_reward",
     gauge_ng, reward_token_address, distributor_address),
    (gauge_tricryptolama, "add_reward",
     reward_token_address, distributor_address)
    # ("target", "fn_name", *args),
]



# description of the vote, will be pinned to IPFS
DESCRIPTION = "Set reward token (wsteh) and distributor_address (Lido: Rewards Committee Multisig) to the stETH-ng and  tricryptolama gauge"


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



def pre_simulate():

    '''
    Mainnet - Curve - stETH-ETH:
    Pool: 0xdc24316b9ae028f1497c275eb9192a3ea0f67022
    Multisig: 0x87D93d9B2C672bf9c9642d853a8682546a5012B5
    Reward Token: 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0
    Gauge: 0x182b723a58739a9c974cfdb385ceadb237453c28

    Pool NG: 0x21E27a5E5513D6e65C4f830167390997aA84843a
    Gauge NG: 0x79F21BC30632cd40d2aF8134B469a0EB4C9574AA
    '''
    # wsteh
    reward_token_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    # Lido: Rewards Committee Multisig 
    distributor_address = "0x87D93d9B2C672bf9c9642d853a8682546a5012B5"

    gauge_address = "0x79F21BC30632cd40d2aF8134B469a0EB4C9574AA"

    gauge_factory = "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"

    gauge_factory_admin = "0x742C3cF9Af45f91B109a81EfEaf11535ECDe9571"

    gauge_tricryptolama = "0x60d3d7ebbc44dc810a743703184f062d00e6db7e"

    gauge_tricryptolama_factory = "0x0c0e5f2fF0ff18a3be9b835635039256dC4B4963"


    # https://etherscan.io/address/0x79f21bc30632cd40d2af8134b469a0eb4c9574aa#writeContract

    gauge_tricryptolama_evm = Contract(gauge_tricryptolama)


    gauge_tricryptolama_factory_evm = Contract(gauge_tricryptolama_factory)

    gauge_tricryptolama_factory_admin = gauge_tricryptolama_factory_evm.admin()
    print(f"ownership_admin: {gauge_tricryptolama_factory_admin}")

    gauge_tricryptolama_evm.add_reward(reward_token_address, distributor_address, {'from': gauge_tricryptolama_factory_admin})


    # read = gauge_tricryptolama_factory_evm.gauge_manager(gauge_address)

    #  print(f"gauge_manager: {read}")

    #gauge_tricryptolama_factory_evm.add_reward(gauge_address, reward_token_address, distributor_address, {'from': admin})

    sys.exit()
    ''' set the same, but directly over gauge, fails bc set above '''
    read = gauge_evm.reward_data(reward_token_address)
    print(read)

    read = gauge_evm.reward_tokens(0)
    print(read)

    gauge_evm.add_reward(reward_token_address, distributor_address, {'from': gauge_factory_admin})
    
    chain.sleep(600)
    
    print("Checking results of this")

    read = gauge_evm.reward_data(reward_token_address)
    print(read)

    read = gauge_evm.reward_tokens(0)
    print(read)


def simulate():
    # only do this if the VECRV_WHALE is not set
    if VECRV_WHALE is None:
        # fetch the top holders so we can pass the vote
        data = requests.get(
            f"https://api.ethplorer.io/getTopTokenHolders/{TARGET['token']}",
            params={"apiKey": APIKEY_ETHPLORER, "limit": 100},
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
    else:
        holders = [VECRV_WHALE]
    
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