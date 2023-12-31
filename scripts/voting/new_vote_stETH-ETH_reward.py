import json
import warnings
import os

import requests
from brownie import Contract, accounts, chain, network, config
from brownie import StakingRewards, CurveLiquidityFarmingManager
from brownie.convert import to_address
from hexbytes import HexBytes

config['autofetch_sources'] = True

warnings.filterwarnings("ignore")

VECRV_WHALE = os.getenv('VECRV_WHALE')
APIKEY_ETHPLORER = os.getenv('APIKEY_ETHPLORER')
IPFS_PROJECT_ID = os.getenv('IPFS_PROJECT_ID')
IPFS_PROJECT_SECRET = os.getenv('IPFS_PROJECT_SECRET')
MAINNET_ADDRESS = os.getenv('MAINNET_ADDRESS')




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

# SENDER = accounts.at('MAINNET_ADDRESS', force=True)

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


# wsteth
reward_token_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
reward_token_address_name = "wstETH"
# Lido: Rewards Committee Multisig 
distributor_address = "0x87D93d9B2C672bf9c9642d853a8682546a5012B5"

# old steth pool
gauge_old = "0x182B723a58739a9c974cFDB385ceaDb237453c28"
gauge_old_token_name = "ETH/stETH Gauge Deposit Token"
gauge_old_admin = "0x519AFB566c05E00cfB9af73496D00217A630e4D5"
old_lp_token = "0x06325440D014e39736583c165C2963BA99fAf14E"
old_lp_token_name = "ETH/stETH LP Token"
old_lp_whale = "0x1C3CB7e3920C77EBA162Cf044F418a854C12fFEf"
old_reward_token = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32" # lido token
old_reward_token_name = "LDO"


# stETH ng
gauge_ng = "0x79F21BC30632cd40d2aF8134B469a0EB4C9574AA"
gauge_factory_ng = "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
gauge_factory_admin_ng = "0x742C3cF9Af45f91B109a81EfEaf11535ECDe9571"
ng_lp_token = "0x21E27a5E5513D6e65C4f830167390997aA84843a"
ng_lp_whale = "0x79F21BC30632cd40d2aF8134B469a0EB4C9574AA"


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
tricryptolama_lp_token = "0x2889302a794dA87fBF1D6Db415C1492194663D13"
tricryptolama_lp_whale = "0x60d3d7eBBC44Dc810A743703184f062d00e6dB7e"



def deploy_oldpools_contracts():

    # msg.sender is set to owner
    # start with this, because we need curve_liquidity_farming_manager address from deployed StakingRewards

    CurveLiquidityFarmingManagerEvm = CurveLiquidityFarmingManager.deploy({'from': accounts[0]})


    owner = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c" # Lido agent
    curve_liquidity_farming_manager = CurveLiquidityFarmingManagerEvm # old one 0x753D5167C31fBEB5b49624314d74A957Eb27170
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
    CurveLiquidityFarmingManagerEvm.set_rewards_contract(StakingRewardsEvm)
    # set ownership to Lido agent
    CurveLiquidityFarmingManagerEvm.transfer_ownership(owner)

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
    reward_tokens = [old_reward_token, reward_token_address, empty, empty, empty, empty, empty, empty]
    gauge_old = "0x182B723a58739a9c974cFDB385ceaDb237453c28"

    # gauge_old_evm = Contract(gauge_old)
    # gauge_old_evm.set_rewards(StakingRewardsEvm, signature, reward_tokens, {'from': gauge_old_admin}   )

    # gauge_old_admin_evm = Contract(gauge_old_admin)
    # gauge_old_admin_evm.set_rewards(gauge_old, StakingRewardsEvm, signature, reward_tokens, {'from': TARGET["agent"]})

    return(StakingRewardsEvm, signature, reward_tokens, CurveLiquidityFarmingManagerEvm)


def mainnet_oldpools_contracts():

    #owner = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c" # Lido agent

    reward_multisig = distributor_address # Lido: Rewards Committee Multisig

    deployer = "0xbF6b125933EC0da01Ac79486935453e534fDc7e1"

    # CurveLiquidityFarmingManager.vy Deployed by Lido https://etherscan.io/address/0x9d81153ae611aeb53e5f137b701c67c2ebffcdae

    CurveLiquidityFarmingManager = "0x9d81153ae611aeb53e5f137b701c67c2ebffcdae"

    CurveLiquidityFarmingManagerEvm = Contract(CurveLiquidityFarmingManager)

    # StakingRewards.sol Deployed by Lido https://etherscan.io/address/0x4f48031b0ef8accea3052af00a3279fba31b50d8

    StakingRewards = "0x4f48031b0ef8accea3052af00a3279fba31b50d8"

    StakingRewardsEvm = Contract(StakingRewards)

    print(f"StakingRewardsAddress: {StakingRewardsEvm}")
    '''
    try:
        StakingRewardsEvm.setRewardsDuration(86400*2, {'from': accounts[0]})
    except:
        print(f"This error is expectd as only owner can call setRewardsDuration() \n ")

    try:
        StakingRewardsEvm.setRewardsDuration(86400*2, {'from': deployer})
    except:
        print(f"This error is expectd as only owner can call setRewardsDuration() \n ")
    '''

    StakingRewardsEvm.setRewardsDuration( 86400*7, {'from': reward_multisig}) 
    
    # set rewards_contract to StakingRewards
    CurveLiquidityFarmingManagerEvm.set_rewards_contract(StakingRewardsEvm, {'from': deployer})
    # set ownership to Lido agent
    CurveLiquidityFarmingManagerEvm.transfer_ownership(reward_multisig, {'from': deployer})

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


    if signature != signature_old:
        print(f"Signature is different, that should not be \n ")
        sys.exit()

    empty = "0x0000000000000000000000000000000000000000"
    reward_tokens = [old_reward_token, reward_token_address, empty, empty, empty, empty, empty, empty]
    # reward_tokens = [reward_token_address, old_reward_token, empty, empty, empty, empty, empty, empty]

    return(StakingRewardsEvm, signature, reward_tokens, CurveLiquidityFarmingManagerEvm)


def mainnet_oldpools_contracts_hardcoded():

    CurveLiquidityFarmingManager = "0x9d81153ae611aeb53e5f137b701c67c2ebffcdae"

    StakingRewards = "0x4f48031b0ef8accea3052af00a3279fba31b50d8"

    signature = "a694fc3a2e1a7d4d3d18b9120000000000000000000000000000000000000000"

    empty = "0x0000000000000000000000000000000000000000"

    reward_tokens = [old_reward_token, reward_token_address, empty, empty, empty, empty, empty, empty]

    return(StakingRewards, signature, reward_tokens, CurveLiquidityFarmingManager)


# if mainnet
if network.show_active() == 'mainnet' or network.show_active() == 'frame':
    StakingRewardsEvm, signature, reward_tokens, CurveLiquidityFarmingManagerEvm = mainnet_oldpools_contracts_hardcoded()
else:
    # with mainnet deployed contracts
    StakingRewardsEvm, signature, reward_tokens, CurveLiquidityFarmingManagerEvm = mainnet_oldpools_contracts()
    # with local deployed contracts
    # StakingRewardsEvm, signature, reward_tokens = deploy_oldpools_contracts()


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
DESCRIPTION = "Configure stETH/ETH old pool to use wstETH as reward token with new Staking Rewards and Curve Liquidity Farming Manager Contract / set reward token (wstETH) and distributor_address (Lido: Rewards Committee Multisig) to the stETH-ng and TricryptoLLAMA gauge"

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

    if network.show_active() == 'mainnet' or network.show_active() == 'frame' :
        kw = {'from': sender, 'priority_fee': '1 gwei' }
        # kw = {'from': sender, 'priority_fee': '1 gwei', 'gas_price' : '9 gwei', 'gas_limit' : '1000000', 'Nonce' : 21, 'allow_revert' : True}

    else:
        kw = {'from': sender}

    # for testing
    fix_ipfs_hash = "QmbmKk7xDjpsZAuGwBVCCCaLudPrJ42uKWcHmavgo5Ba74"

    if fix_ipfs_hash == "QmbmKk7xDjpsZAuGwBVCCCaLudPrJ42uKWcHmavgo5Ba74":
        ipfs_hash = fix_ipfs_hash
    else:
        text = json.dumps({"text": DESCRIPTION})
        session = requests.Session()
        session.auth = (IPFS_PROJECT_ID, IPFS_PROJECT_SECRET)
        response = session.post("https://ipfs.infura.io:5001/api/v0/add", files={"file": text})
        ipfs_hash = response.json()["Hash"]

    print(f"ipfs hash: {ipfs_hash}")
    print(f"ipfs url: https://ipfs.io/ipfs/{ipfs_hash}")

    
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

def test_farm_token(gauge, reward_token, distributor, lp_token, lp_token_whale, gauge_token_holder = "0x"):

    # send LP token to contract and test farming reward
    
    gauge_evm = Contract(gauge)
    reward_token_evm = Contract(reward_token)
    reward_token_name = reward_token_address_name
    lp_token_evm = Contract(lp_token)
    lp_token_name = "LP token"


    # send reward token
    amount = 120 * 10**18
    reward_token_evm.approve(gauge, amount, {'from': distributor} )
    gauge_evm.deposit_reward_token(reward_token, 20 * 10**18,  {'from': distributor} )
   

    # deposit lp token
    if gauge_token_holder == "0x":
        lp_account = accounts[0]
        lp_token_whale = accounts.at(lp_token_whale, force=True)    
        
        lp_amount = 200 * 10**18
        
        lp_token_evm.approve(gauge, lp_amount, {'from': lp_account} )
        # lp_token_evm.transfer.info()    
        lp_token_evm.transfer(lp_account, lp_amount, {'from': lp_token_whale})

        getBalance("balance before gauge.deposit()", lp_token_evm, lp_account, lp_token_name)
        gauge_evm.deposit(lp_amount, {'from': lp_account})
        getBalance("balance after gauge.deposit()", lp_token_evm, lp_account, lp_token_name)
        print( reward_token_evm.balanceOf(lp_account) )

    else:
        # with existing lp in gauge
        lp_account = accounts.at(gauge_token_holder, force=True)   

        lp_amount = 1 * 10**18
        
        lp_token_evm.approve(gauge, lp_amount, {'from': lp_account} )
        #gauge_evm.approve(lp_token, lp_amount, {'from': lp_account} )

        # lp_token_evm.transfer(lp_account, lp_amount, {'from': lp_token_whale})
        '''
        # deposit and withdraw gives a small reward on day 1 (reward of 1 block)
        getBalance("balance before gauge.deposit()", lp_token_evm, lp_account, lp_token_name)
        #gauge_evm.deposit(lp_amount, {'from': lp_account})
        getBalance("balance after gauge.deposit()", lp_token_evm, lp_account, lp_token_name)

        getBalance("balance before gauge.withdraw()", lp_token_evm, lp_account, lp_token_name)
        #gauge_evm.withdraw(lp_amount, {'from': lp_account})
        getBalance("balance after withdraw.withdraw()", lp_token_evm, lp_account, lp_token_name)
        '''
        
    for day in range(1 , 12):
        print(f"\nafter day: {day} ------------------------------------------------------------------")
        chain.sleep(86400)
        # claimable_reward = arbi_gauge_evm.claimable_reward(lp_account, arbi_reward_token_address)/10**18
        # print(f"claimable_reward() {claimable_reward}")

        balance_before = getBalance("balance before gauge.claim_rewards()", reward_token_evm, lp_account, reward_token_name)
        gauge_evm.claim_rewards({'from': lp_account} )
        balance = getBalance("balance after gauge.claim_rewards()", reward_token_evm, lp_account, reward_token_name)

        diff = balance - balance_before
        print(f"balance diff for {reward_token_address_name}: {diff/10**18}")

        if day == 4:
            balance = getBalance("balance before gauge.deposit_reward_token()", reward_token_evm, lp_account, lp_token_name)
            gauge_evm.deposit_reward_token(reward_token, 40 * 10**18,  {'from': distributor} )
            balance = getBalance("balance after gauge.deposit_reward_token()", reward_token_evm, lp_account, lp_token_name)

        claimed_reward = gauge_evm.claimed_reward(lp_account, reward_token)/10**18
        print(f"claimed_reward() {claimed_reward}")


def start_steth_old(gauge, reward_token, distributor, lp_token, lp_token_whale, StakingRewardsEvm, CurveLiquidityFarmingManagerEvm):

    reward_token_evm = Contract(reward_token)
    reward_token_name = reward_token_address_name
    lp_token_evm = Contract(lp_token)
    lp_token_name = old_lp_token_name

    # send reward token
    amount = 50 * 10**18

    reward_token_evm.approve(gauge, amount, {'from': distributor} )
    reward_token_evm.transfer(CurveLiquidityFarmingManagerEvm, amount, {'from': distributor})
    CurveLiquidityFarmingManagerEvm.start_next_rewards_period(  {'from': distributor}  )

    gauge_evm = Contract(gauge)
    gauge_token_name = gauge_old_token_name
    
    lp_token_whale = accounts.at(lp_token_whale, force=True)    
    
    lp_amount = 200 * 10**18
    if False:
        lp_account = accounts[0]
        

        lp_token_evm.approve(gauge, lp_amount, {'from': lp_account} )

        getBalance("balance before lp_token_evm.transfer()", lp_token_evm, lp_token_whale, lp_token_name)
        getBalance("balance before lp_token_evm.transfer()", gauge_evm, lp_token_whale, gauge_token_name)
    
        lp_token_evm.transfer(lp_account, lp_amount, {'from': lp_token_whale})

        # lp_token_evm.approve(StakingRewardsEvm, lp_amount, {'from': lp_account} )
        # lp_tokenlp_token_evm.approve(lp_account, lp_amount, {'from': lp_account} )

        getBalance("balance before gauge.deposit()", lp_token_evm, lp_account, lp_token_name)
        getBalance("balance before gauge.deposit()", gauge_evm, lp_account, gauge_token_name)
        gauge_evm.deposit(lp_amount, {'from': lp_account})
        getBalance("balance after gauge.deposit()", lp_token_evm, lp_account, lp_token_name)
        getBalance("balance before gauge.deposit()", gauge_evm, lp_account, gauge_token_name)
    else:
        lp_account = "0xc2720997ea2ea9baad61e8f7de8ca3b5a1bbe1b3"

    # with Lido reward unwithdrawed
    old_staking_account = "0xc2720997ea2ea9baad61e8f7de8ca3b5a1bbe1b3"
    '''
    print(f"old_staking_account: {old_staking_account}" )

    ad_with_old_reward = accounts.at(old_staking_account, force=True) 
    getBalance("balance before gauge.deposit()", lp_token_evm, ad_with_old_reward, lp_token_name)
    # deposit withdraws old LDO token
    gauge_evm.deposit(10 * 10**18, {'from': ad_with_old_reward})
    getBalance("balance after gauge.deposit()", lp_token_evm, ad_with_old_reward, lp_token_name)
    '''
    # print( reward_token_evm.balanceOf(lp_account) )

    for day in range(1 , 15):
        print(f"\nafter day: {day} ------------------------------------------------------------------")
        chain.sleep(86400)
        # also claims token
        # claimable eward = gauge_evm.claimable_reward(lp_account, reward_token )/10**18
        # print(f"claimable_reward() {claimable_reward}")

        balance_before = getBalance("balance before gauge.claim_rewards()", reward_token_evm, lp_account, reward_token_name)
        gauge_evm.claim_rewards({'from': lp_account} )
        balance = getBalance("balance after gauge.claim_rewards()", reward_token_evm, lp_account, reward_token_name)

        diff = balance - balance_before
        print(f"Belance diff for wstETH: {diff/10**18}")

        # start next rewards period
        if day == 8:
            try:
                reward_token_evm.transfer(CurveLiquidityFarmingManagerEvm, 100 * 10**18,  {'from': distributor})
                CurveLiquidityFarmingManagerEvm.start_next_rewards_period(  {'from': distributor}  )
            except:
                print(f" if not finished, will fail, see error above")

        if day == 10:   
            old_reward_token = Contract('0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32')
            old_reward_token_name = "LDO"
            empty = "0x0000000000000000000000000000000000000000"
            reward_tokens = [old_reward_token, empty, empty, empty, empty, empty, empty, empty]
            getBalance("balance before gauge.claim_historic_rewards()", old_reward_token, old_staking_account, old_reward_token_name)
            gauge_evm.claim_historic_rewards(reward_tokens, {'from': lp_account})

            getBalance("balance after gauge.claim_historic_rewards", old_reward_token, old_staking_account, old_reward_token_name)

            # withdraw half of lp
            getBalance("balance before gauge.withdraw()", lp_token_evm, lp_account, lp_token_name)
            getBalance("balance before gauge.withdraw()", gauge_evm, lp_account, gauge_token_name)

            getBalance("balance before gauge.withdraw()", reward_token_evm, old_staking_account, reward_token_address_name)
            getBalance("balance before gauge.withdraw()", lp_token_evm, old_staking_account, old_lp_token_name) 
            gauge_evm.withdraw(1 * 10**18, {'from': lp_account} )
            getBalance("balance after gauge.withdraw()", lp_token_evm, lp_account, lp_token_name)
            getBalance("balance after gauge.withdraw()", gauge_evm, lp_account, gauge_token_name)
  
        if day == 12:
            # withdraw the rest of lp
            getBalance("balance before gauge.withdraw()", lp_token_evm, lp_account, lp_token_name)
            getBalance("balance before gauge.withdraw()", gauge_evm, lp_account, gauge_token_name)
            gauge_evm.withdraw(5 * 10**18, {'from': lp_account} )
            getBalance("balance after gauge.withdraw()", lp_token_evm, lp_account, lp_token_name)
            getBalance("balance after gauge.withdraw()", gauge_evm, lp_account, gauge_token_name)

        # claimed_reward = gauge_evm.claimed_reward(accounts[0], reward_token)/10**18
        # print(f"claimed_reward() {claimed_reward}")


def convex_old_staking(old_lp_token, old_lp_whale, after_vote):
    
    cvx_steth_pool = Contract("0x0A760466E1B4621579a82a39CB56Dda2F4E70f03")
    cvx_boster = Contract("0xF403C135812408BFbE8713b5A23a04b3D48AAE31")
    ExtraRewardStashV2 = Contract("0x9710fD4e5CA524f1049EbeD8936c07C81b5EAB9f")
    old_lp_token_evm = Contract(old_lp_token)
    crv_evm = Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")
    old_reward_token_evm =  Contract(old_reward_token)
    reward_token_address_evm = Contract(reward_token_address)


    if after_vote == False:

        lp_amount = 200 * 10**18

        lp_account = accounts.at(old_lp_whale, force=True) 

        old_lp_token_evm.approve(cvx_boster, 300 * 10**18, {'from': lp_account} )
        '''
        getBalance("balance before cvx_boster.deposit(25, {lp_amount})", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        tx = cvx_boster.deposit( 25, lp_amount, 1, { 'from': lp_account } )
        getBalance("balance after cvx_boster.deposit()", old_lp_token_evm, old_lp_whale, old_lp_token_name)

        print(*tx.events, sep='\n')
        '''

        full_amount = getBalance("balance before cvx_boster.depositAll(25, 1)", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        tx = cvx_boster.depositAll( 25, 1, { 'from': lp_account } )
        getBalance("balance after cvx_boster.depositAll(25)", old_lp_token_evm, old_lp_whale, old_lp_token_name)

        print(*tx.events, sep='\n')
        chain.sleep(86400 * 1)

        getBalance("balance before cvx_steth_pool.withdrawAndUnwrap", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        tx = cvx_steth_pool.withdrawAndUnwrap(full_amount, 1, { 'from': lp_account } )
        getBalance("balance after cvx_steth_pool.withdrawAndUnwrap", old_lp_token_evm, old_lp_whale, old_lp_token_name)

        print(*tx.events, sep='\n')

        '''
        getBalance("balance before cvx_boster.withdrawAll(25)", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        tx = cvx_boster.withdrawAll( 25, { 'from': lp_account } )
        getBalance("balance after cvx_boster.withdrawAll(25)", old_lp_token_evm, old_lp_whale, old_lp_token_name)

        print(*tx.events, sep='\n')

        getBalance("balance before cvx_boster.withdraw()", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        cvx_boster.withdraw( 25, lp_amount, { 'from': lp_account } )
        getBalance("balance after cvx_boster.withdraw()", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        '''
 
    
    print(f"cvx_steth_pool: {cvx_steth_pool}")

    extraRewards = cvx_steth_pool.extraRewards(0)
    print(f"cvx_steth_pool.extraRewards(0): {extraRewards}")

    extraRewardsLength = cvx_steth_pool.extraRewardsLength()
    print(f"cvx_steth_pool.extraRewardsLength(): {extraRewardsLength}")

    print(f"ExtraRewardStashV2: {ExtraRewardStashV2}")
    tokenCount = ExtraRewardStashV2.tokenCount()
    print(f"ExtraRewardStashV2.tokenCount()): {tokenCount}")

    tokenInfo = ExtraRewardStashV2.tokenInfo(0)
    print(f"ExtraRewardStashV2.tokenInfo(0)): {tokenInfo}")

    print(f"cvx_boster: {cvx_boster}")

    poolInfo = cvx_boster.poolInfo(25)
    print(f"cvx_boster.poolInfo(25): {poolInfo}")
    print(f"cvx_boster.poolInfo(25).stash: {poolInfo[4]}")

    print(f"call cvx_boster.earmarkRewards(25)")

    tx = cvx_boster.earmarkRewards(25, {'from': accounts[0]})
    print(*tx.events, sep='\n')

    poolInfo = cvx_boster.poolInfo(25)
    print(f"cvx_boster.poolInfo(25): {poolInfo}")
    print(f"cvx_boster.poolInfo(25).stash: {poolInfo[4]}")

    extraRewards = cvx_steth_pool.extraRewards(0)
    print(f"cvx_steth_pool.extraRewards(0): {extraRewards}")

    if after_vote == True:
        extraRewards = cvx_steth_pool.extraRewards(1)
        print(f"cvx_steth_pool.extraRewards(1): {extraRewards}")

        extraRewardsLength = cvx_steth_pool.extraRewardsLength()
        print(f"cvx_steth_pool.extraRewardsLength(): {extraRewardsLength}")

    tokenCount = ExtraRewardStashV2.tokenCount()
    print(f"ExtraRewardStashV2.tokenCount()): {tokenCount}")

    tokenInfo = ExtraRewardStashV2.tokenInfo(0)
    print(f"ExtraRewardStashV2.tokenInfo(0)): {tokenInfo}")
    
    if after_vote == True:

        tokenInfo = ExtraRewardStashV2.tokenInfo(1)
        print(f"ExtraRewardStashV2.tokenInfo(1)): {tokenInfo}")

    if after_vote == True:

        # send reward token
        amount = 50 * 10**18

        reward_token_evm = Contract(reward_token_address)
        reward_token_evm.approve(gauge_old, amount, {'from': distributor_address} )
        reward_token_evm.transfer(CurveLiquidityFarmingManagerEvm, amount, {'from': distributor_address})
        
        StakingRewardsEvm.setRewardsDuration(86400*7, {'from': distributor_address} )

        CurveLiquidityFarmingManagerEvm.start_next_rewards_period(  {'from': distributor_address}  )

        lp_amount = 200 * 10**18

        lp_account = accounts.at(old_lp_whale, force=True) 

        old_lp_token_evm.approve(cvx_boster, 300 * 10**18, {'from': lp_account} )
        '''
        getBalance("balance before cvx_boster.deposit(25, {lp_amount})", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        tx = cvx_boster.deposit( 25, lp_amount, 1, { 'from': lp_account } )
        getBalance("balance after cvx_boster.deposit()", old_lp_token_evm, old_lp_whale, old_lp_token_name)

        print(*tx.events, sep='\n')
        '''
        
        full_amount = getBalance("balance before cvx_boster.depositAll(25, 1)", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        tx = cvx_boster.depositAll( 25, 1, { 'from': lp_account } )
        getBalance("balance after cvx_boster.depositAll(25)", old_lp_token_evm, old_lp_whale, old_lp_token_name)

        print(*tx.events, sep='\n')

        cvx_boster.earmarkRewards(25, {'from': accounts[0]})
        tx = cvx_boster.earmarkRewards(25, {'from': accounts[0]})
        print(*tx.events, sep='\n')

        tokenInfo = ExtraRewardStashV2.tokenInfo(1)
        print(f"ExtraRewardStashV2.tokenInfo(1)): {tokenInfo}")


        chain.sleep(86400 * 7)

        getBalance("balance before cvx_steth_pool.withdrawAndUnwrap()", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        getBalance("balance before cvx_steth_pool.withdrawAndUnwrap()", crv_evm, old_lp_whale, "CRV")
        getBalance("balance before cvx_steth_pool.withdrawAndUnwrap()", old_reward_token_evm, old_lp_whale, old_reward_token_name)
        getBalance("balance before cvx_steth_pool.withdrawAndUnwrap()", reward_token_address_evm, old_lp_whale, reward_token_address_name)

        tx = cvx_steth_pool.withdrawAndUnwrap(full_amount, 1, { 'from': lp_account } )

        getBalance("balance after cvx_steth_pool.withdrawAndUnwrap", old_lp_token_evm, old_lp_whale, old_lp_token_name)
        getBalance("balance after cvx_steth_pool.withdrawAndUnwrap()", crv_evm, old_lp_whale, "CRV")
        getBalance("balance after cvx_steth_pool.withdrawAndUnwrap()", old_reward_token_evm, old_lp_whale, old_reward_token_name)
        getBalance("balance after cvx_steth_pool.withdrawAndUnwrap()", reward_token_address_evm, old_lp_whale, reward_token_address_name)

        

        print(*tx.events, sep='\n')


        

def withdraw_reward_old_staking(mode, gauge, old_lp_token, old_reward_token):

    '''
    0x7568650de016ef3c9718fd5eb57e8c274d709567 : 16205837785234663607
    0xc2720997ea2ea9baad61e8f7de8ca3b5a1bbe1b3 : 90771021611203357683
    0x7535ea43184db443ceb08bece981bfe2fec07956 : 9000000000000000000
    '''

    gauge = Contract(gauge)
    gauge_token_name = gauge_old_token_name

    old_reward_token_evm = Contract(old_reward_token)

    empty = "0x0000000000000000000000000000000000000000"
    reward_tokens = [old_reward_token, empty, empty, empty, empty, empty, empty, empty]

    if mode == 'before':
        old_staking_account = "0xc2720997ea2ea9baad61e8f7de8ca3b5a1bbe1b3"
    elif mode == 'after':
        old_staking_account = "0x7535ea43184db443ceb08bece981bfe2fec07956"
    elif mode == 'after new':
        old_staking_account = "0xc2720997ea2ea9baad61e8f7de8ca3b5a1bbe1b3"

    print(f"old_staking_account: {old_staking_account}" )

    ad_with_old_reward = accounts.at(old_staking_account, force=True) 

    reward_integral_for = gauge.reward_integral_for(old_reward_token, old_staking_account)

    print(f"reward_integral_for: {reward_integral_for}")

    balance = getBalance("balance before gauge.withdraw()", gauge, old_staking_account, gauge_token_name)
    getBalance("balance before gauge.withdraw()", old_reward_token_evm, old_staking_account, old_reward_token_name)

    if mode == 'after new':
        reward_token_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
        reward_token_address_name = "wstETH"
        reward_token_evm = Contract(reward_token_address)
  
        old_lp_token_evm = Contract(old_lp_token)

        getBalance("balance before gauge.withdraw()", reward_token_evm, old_staking_account, reward_token_address_name)
        getBalance("balance before gauge.withdraw()", old_lp_token_evm, old_staking_account, old_lp_token_name) 

    gauge.withdraw(balance, {'from': ad_with_old_reward} )

    getBalance("balance after gauge.withdraw()", gauge, old_staking_account, gauge_token_name)
    getBalance("balance after gauge.withdraw()", old_reward_token_evm, old_staking_account, old_reward_token_name)

    if mode == 'after new':
        getBalance("balance after gauge.withdraw()", reward_token_evm, old_staking_account, reward_token_address_name)
        getBalance("balance after gauge.withdraw()", old_lp_token_evm, old_staking_account, old_lp_token_name) 

    if mode == 'after':
        getBalance("balance before gauge.claim_historic_rewards()", old_reward_token_evm, old_staking_account, old_reward_token_name)

        gauge.claim_historic_rewards(reward_tokens, {'from': ad_with_old_reward})

        getBalance("balance after gauge.claim_historic_rewards", old_reward_token_evm, old_staking_account, old_reward_token_name)

    if mode == 'before':
        getBalance("balance before gauge.claim_rewards()", old_reward_token_evm, old_staking_account, old_reward_token_name)

        gauge.claim_rewards({'from': ad_with_old_reward})

        getBalance("balance after gauge.claim_rewards()", old_reward_token_evm, old_staking_account, old_reward_token_name)

        reward_integral_for = gauge.reward_integral_for(old_reward_token, old_staking_account)
        print(f"reward_integral_for: {reward_integral_for}")


def decode_vote(aragon, vote_id):

    script = HexBytes(aragon.getVote(vote_id)["script"])

    idx = 4
    while idx < len(script):
        target = Contract(script[idx : idx + 20])
        idx += 20
        length = int(script[idx : idx + 4].hex(), 16)
        idx += 4
        calldata = script[idx : idx + length]
        idx += length
        fn, inputs = target.decode_input(calldata)
        if calldata[:4].hex() == "0xb61d27f6":
            agent_target = Contract(inputs[0])
            fn, inputs = agent_target.decode_input(inputs[2])
            print(
                f"Call via agent ({target}):\n ├─ To: {agent_target}\n"
                f" ├─ Function: {fn}\n └─ Inputs: {inputs}\n"
            )
        else:
            print(f"Direct call:\n ├─ To: {target}\n ├─ Function: {fn}\n └─ Inputs: {inputs}")



def getBalance(note, contract, address, tokenname):
        print(f"\nstate: {tokenname} {note}")
        print(f"address: {address}")
        balance = contract.balanceOf(address)
        print(f"token: {contract}")
        print(f"balance int: {balance}")
        print(f"balance    : {balance/10**18} \n")
        return balance


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

    # convex_old_staking(old_lp_token, old_lp_whale, after_vote = False)
    
    aragon = Contract(TARGET["voting"])
    for acct in holders:
        aragon.vote(vote_id, True, False, {"from": acct})
    
    # sleep for a week so it has time to pass
    chain.sleep(86400 * 7)

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, {"from": top_holder})
    

    convex_old_staking(old_lp_token, old_lp_whale, after_vote = True)

    sys.exit()

    print(f"Start withdraw_reward_old_staking() after ####################################### \n")
    # withdraw_reward_old_staking('after', gauge_old, old_lp_token, old_reward_token)
    print(f"End withdraw_reward_old_staking() after  ####################################### \n")

    # stETH old
    
    print(f"Start test stETH old (ETH/stETH) pool ####################################### \n")
    start_steth_old(gauge_old, reward_token_address, distributor_address, old_lp_token, old_lp_whale, StakingRewardsEvm, CurveLiquidityFarmingManagerEvm)
    print(f"End test stETH old (ETH/stETH) pool ####################################### \n")
    
    print(f"Start withdraw_reward_old_staking() after new ####################################### \n")
    # withdraw_reward_old_staking('after new', gauge_old, old_lp_token, old_reward_token)
    print(f"End withdraw_reward_old_staking() after new ####################################### \n")

    # stETH new
    print(f"Start test reward stETH-ng (ETH/stETH) pool ####################################### \n")
    # 0xaD3d0a6868124F3f28fc746132Bc32608f0E6a60 has unstaked lp token
    #test_farm_token(gauge_ng, reward_token_address, distributor_address, ng_lp_token, ng_lp_whale, "0xaD3d0a6868124F3f28fc746132Bc32608f0E6a60")
    # 0x4d6DF8cdBD27461c968C76c3F278f6749afFa541 has token in gauge
    test_farm_token(gauge_ng, reward_token_address, distributor_address, ng_lp_token, ng_lp_whale, "0x4d6DF8cdBD27461c968C76c3F278f6749afFa541")
    
    print(f"End test reward stETH-ng (ETH/stETH) pool ####################################### \n")

    # tricryptolama
    print(f"Start test reward TricryptoLLAMA (crvUSD/tBTC/wstETH) pool ####################################### \n")
    #test_farm_token(gauge_tricryptolama, reward_token_address, distributor_address, tricryptolama_lp_token, tricryptolama_lp_whale, tricryptolama_lp_whale)
    print(f"End test reward TricryptoLLAMA (crvUSD/tBTC/wstETH) pool ####################################### \n")

