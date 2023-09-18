all:

delete_networks:
	brownie networks delete mainnet
	brownie networks delete hardhat-fork-curve
	brownie networks delete arbitrum-main
	brownie networks delete arbitrum-fork
	brownie networks delete optimism-main
	brownie networks delete optimism-fork

import_networks:
	brownie networks import brownie-config.yaml

mainnet_reward:
	brownie run scripts/voting/new_vote_stETH-ETH_reward.py simulate --network hardhat-fork-curve


arbitrum_reward:
	brownie run scripts/sidechain/set_wsteth-eth_arbitrum_reward.py simulate --network arbitrum-fork

optimism_reward:
	brownie run scripts/sidechain/set_wsteth-eth_optimism_reward.py simulate --network optimism-fork

mainnet_old_steth_pool:
	brownie run scripts/voting/deploy_staking_reward.py --network hardhat-fork-curve

arbitrum_console:
	brownie console --network arbitrum-fork
