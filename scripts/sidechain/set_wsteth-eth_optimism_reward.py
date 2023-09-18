import json
import warnings

import requests
from brownie import Contract, accounts, chain, network, config
from brownie.convert import to_address


config['autofetch_sources'] = True

# warnings.filterwarnings("ignore")

def main():
    self.simulate()

def simulate():

# Optimism - Curve - wstETH-ETH:
# Pool: 0xb90b9b1f91a01ea22a182cd84c1e22222e39b415
# Multisig: 0x5033823F27c5f977707B58F0351adcD732C955Dd
# Reward Token: 0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb // https://optimistic.etherscan.io/address/0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb
# Gauge: 0xd53ccbfed6577d8dc82987e766e75e3cb73a8563 // https://optimistic.etherscan.io/address/0xd53ccbfed6577d8dc82987e766e75e3cb73a8563
# Factory: 0xabC000d88f23Bb45525E447528DBF656A9D55bf5  // https://optimistic.etherscan.io/address/0xabC000d88f23Bb45525E447528DBF656A9D55bf5
# Gauge Manager: 0x5033823F27c5f977707B58F0351adcD732C955Dd
    opti_distributor = "0x5033823F27c5f977707B58F0351adcD732C955Dd"
    opti_reward_token_address = "0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb"
    opti_gauge = "0xd53ccbfed6577d8dc82987e766e75e3cb73a8563"
    opti_gauge_manager = opti_distributor


    opti_gauge_evm = Contract(opti_gauge)

    # returns just set distributor address
    
    read = opti_gauge_evm.reward_data(opti_reward_token_address)
    print(f"distributor address on optimism: {read}")

    opti_gauge_evm.add_reward(opti_reward_token_address, opti_distributor, {'from': opti_gauge_manager})

    
    # returns LIDO token on optimism  https://optimistic.etherscan.io/address/0xFdb794692724153d1488CcdBE0C56c252596735F
    read = opti_gauge_evm.reward_tokens(0)
    print(f"LIDO token on optimism: {read}")

    # returns Optimism token on optimism https://optimistic.etherscan.io/address/0x4200000000000000000000000000000000000042
    read = opti_gauge_evm.reward_tokens(1)
    print(f"Optimism token on optimism: {read}")

    # returns just set wsteth token on optimism https://optimistic.etherscan.io/address/0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb
    read = opti_gauge_evm.reward_tokens(2)
    print(f"wsteth token on optimism: {read}")

    # returns empty token on optimism
    read = opti_gauge_evm.reward_tokens(3)
    print(f"empty token on optimism: {read}")

    # returns just set distributor address
    
    read = opti_gauge_evm.reward_data(opti_reward_token_address)
    print(f"distributor address on optimism: {read}")

    # Now let's borrow something
    # First, hack wsteth_whale to do it
    '''
    wsteth_whale = accounts.at("0xc45A479877e1e9Dfe9FcD4056c699575a1045dAA", force=True)
    wsteth = Contract(opti_reward_token_address)
    wsteth.transfer(opti_distributor, 100 * 10**18, {'from': wsteth_whale})

    opti_gauge_evm.deposit_reward_token(opti_reward_token_address, 100 * 18**10 ,  {'from': opti_distributor} )
    '''
    

