import json
import warnings

import requests
from brownie import StakingRewards, CurveLiquidityFarmingManager, Contract, accounts, chain, network, config
from brownie.convert import to_address


'''
Replaying this by deploy fresh contract https://etherscan.io/tx/0x463cc85643784ec6eda246cff1366e8aa0ee964400485c2d5eee25f0e9044edc
'''

config['autofetch_sources'] = True

warnings.filterwarnings("ignore")

def main():
    simulate()

def simulate():
    ''' address _owner,
        address _rewardsDistribution,
        address _rewardsToken,
        address _stakingToken,
        uint256 _rewardsDuration
    '''

    # msg.sender is set to owner
    # start with this, because we need curve_liquidity_farming_manager address from deployed StakingRewards

    CurveLiquidityFarmingManagerEwm = CurveLiquidityFarmingManager.deploy({'from': accounts[0]})


    owner = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c" # Lido agent
    curve_liquidity_farming_manager = CurveLiquidityFarmingManagerEwm # old one 0x753D5167C31fBEB5b49624314d74A957Eb27170
    reward_token_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0" # wsteth
    staking_token = "0x06325440D014e39736583c165C2963BA99fAf14E" # Curve.fi ETH/stETH (steCRV) Token 
    rewards_duration = 86400 * 1 # in Seconds? can be reset with setRewardsDuration()


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