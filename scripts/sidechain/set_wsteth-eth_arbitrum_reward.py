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
# Reward Token Contract: https://arbiscan.io/address/0x0fbcbaea96ce0cf7ee00a8c19c3ab6f5dc8e1921#code
# wsteth/eth LP Token: 0xDbcD16e622c95AcB2650b38eC799f76BFC557a0b

# Gauge: 0x098ef55011b6b8c99845128114a9d9159777d697 // https://arbiscan.io/address/0x098ef55011b6b8c99845128114a9d9159777d697
# Factory: 0xabc000d88f23bb45525e447528dbf656a9d55bf5 // https://arbiscan.io/address/0xabc000d88f23bb45525e447528dbf656a9d55bf5

    arbi_distributor = "0x8C2b8595eA1b627427EFE4f29A64b145DF439d16"
    arbi_reward_token_address = "0x5979D7b546E38E414F7E9822514be443A4800529"
    arbi_gauge = "0x098ef55011b6b8c99845128114a9d9159777d697"
    arbi_gauge_manager = arbi_distributor


    arbi_gauge_evm = Contract(arbi_gauge)

    # returns just set distributor address
    
    
    arbi_gauge_evm.add_reward(arbi_reward_token_address, arbi_distributor, {'from': arbi_gauge_manager})

    # returns LIDO token on arbitrum https://arbiscan.io/address/0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60 
    read = arbi_gauge_evm.reward_tokens(0)
    print(f"LIDO token on arbitrum: {read}")

    # returns just set wsteth token on arbitrum https://arbiscan.io/address/0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60 
    read = arbi_gauge_evm.reward_tokens(1)
    print(f"wsteth token on arbitrum: {read}")

    read = arbi_gauge_evm.reward_data(arbi_reward_token_address)
    print(f"distributor address on arbitrum: {read}")

    # Now let's borrow something
    # First, hack wsteth_whale to do it
    
    wsteth_whale = accounts.at("0x513c7e3a9c69ca3e22550ef58ac1c0088e918fff", force=True)
    wsteth = Contract(arbi_reward_token_address)
    amount = 200 * 10**18
    wsteth.transfer(arbi_distributor, amount, {'from': wsteth_whale})
    wsteth.approve(arbi_gauge, amount, {'from': arbi_distributor} )

    print(wsteth.balanceOf(arbi_distributor))
    amount_sent = 100 * 10**18
    arbi_gauge_evm.deposit_reward_token(arbi_reward_token_address, amount_sent,  {'from': arbi_distributor} )

    week_in_sec = 86400 * 7
    calc_token_rate = amount_sent/week_in_sec
    print(f"token rate per second: {calc_token_rate}")

    distributor, period_finish, rate, last_update, integral = arbi_gauge_evm.reward_data(arbi_reward_token_address)
    print(f"reward_data({arbi_reward_token_address}): distributor: {distributor}, period_finish: {period_finish}, rate: {rate}, last_update: {last_update}, integral: {integral}")

    # send LP token to contract and test 
    lp_token = "0xDbcD16e622c95AcB2650b38eC799f76BFC557a0b"
    lb_otken_whale = accounts.at("0x098ef55011b6b8c99845128114a9d9159777d697", force=True)
    
    lp_amount = 200 * 10**18
    
    lp_token_evm = Contract(lp_token)
    lp_token_evm.transfer(accounts[0], lp_amount, {'from': lb_otken_whale})
    lp_token_evm.approve(arbi_gauge, lp_amount, {'from': accounts[0]} )

    # arbi_gauge_evm.deposit.info()

    arbi_gauge_evm.deposit(lp_amount, {'from': accounts[0]})

    print( wsteth.balanceOf(accounts[0]) )

    for day in range(1 , 18):
        print(f"\nafter day: {day} ------------------------------------------------------------------")
        chain.sleep(86400)
        # claimable_reward = arbi_gauge_evm.claimable_reward(accounts[0], arbi_reward_token_address)/10**18
        # print(f"claimable_reward() {claimable_reward}")
        balance = wsteth.balanceOf(accounts[0])/10**18
        balance_before = balance
        arbi_gauge_evm.claim_rewards({'from': accounts[0]} )
        balance = wsteth.balanceOf(accounts[0])/10**18
        print(f"wallet balance before claim {balance_before}")
        print(f"wallet balance after claim {balance}")
        if day == 4:
            arbi_gauge_evm.deposit_reward_token(arbi_reward_token_address, 50 * 10**18,  {'from': arbi_distributor} )
        diff = balance - balance_before
        print(f"wallet balance diff {diff}")
        claimed_reward = arbi_gauge_evm.claimed_reward(accounts[0], arbi_reward_token_address)/10**18
        print(f"claimed_reward() {claimed_reward}")

    
    # last time:
    # deposit_reward_token LIDO over multisig
    # set the amount of reward tokens for a week
    # https://arbiscan.io/tx/0x90a47b338d2bf6d65ac02ed45fe37f30858e9fc657a69346f4c52648ab7cbdd5