import json
import warnings

import requests
from brownie import Contract, accounts, chain, network, config
from brownie.convert import to_address


config['autofetch_sources'] = True

# warnings.filterwarnings("ignore")


def simulate():

# Arbitrum - Curve - wstETH-ETH:
# Pool: 0x6eb2dc694eb516b16dc9fbc678c60052bbdd7d80
# Multisig: 0x8C2b8595eA1b627427EFE4f29A64b145DF439d16
# Reward Token: 0x5979D7b546E38E414F7E9822514be443A4800529 // wsteth https://arbiscan.io/address/0x5979D7b546E38E414F7E9822514be443A4800529
# Gauge: 0x098ef55011b6b8c99845128114a9d9159777d697 // https://arbiscan.io/address/0x098ef55011b6b8c99845128114a9d9159777d697
# Factory: 0xabc000d88f23bb45525e447528dbf656a9d55bf5 // https://arbiscan.io/address/0xabc000d88f23bb45525e447528dbf656a9d55bf5

    arbi_distributor = "0x8C2b8595eA1b627427EFE4f29A64b145DF439d16"
    arbi_reward_token_address = "0x5979D7b546E38E414F7E9822514be443A4800529"
    arbi_gauge = "0x098ef55011b6b8c99845128114a9d9159777d697"
    arbi_gauge_manager = arbi_distributor

    arbi_gauge_evm = Contract(arbi_gauge)

    # returns just set distributor address
    
    read = arbi_gauge_evm.reward_data(arbi_reward_token_address)
    print(f"distributor address on arbitrum: {read}")

    arbi_gauge_evm.add_reward(arbi_reward_token_address, arbi_distributor, {'from': arbi_gauge_manager})

    # returns LIDO token on arbitrum https://arbiscan.io/address/0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60 
    read = arbi_gauge_evm.reward_tokens(0)
    print(f"LIDO token on arbitrum: {read}")

    # returns just set wsteth token on arbitrum https://arbiscan.io/address/0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60 
    read = arbi_gauge_evm.reward_tokens(1)
    print(f"wsteth token on arbitrum: {read}")

    # returns just set distributor address
    
    read = arbi_gauge_evm.reward_data(arbi_reward_token_address)
    print(f"distributor address on arbitrum: {read}")

    # Now let's borrow something
    # First, hack wsteth_whale to do it
    
    wsteth_whale = accounts.at("0x513c7e3a9c69ca3e22550ef58ac1c0088e918fff", force=True)
    wsteth = Contract(arbi_reward_token_address)
    amount = 100 * 10**18
    wsteth.transfer(arbi_distributor, amount, {'from': wsteth_whale})

    # wsteth.approve(arbi_distributor, amount, {'from': arbi_distributor} )
    arbi_gauge_evm.deposit_reward_token(arbi_reward_token_address, amount,  {'from': arbi_distributor} )

    

