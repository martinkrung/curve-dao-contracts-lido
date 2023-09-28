all:

start_env:
	# source will not work, but this is for cmd documentation
	source .env
	source .venv/bin/activate

delete_networks:
	brownie networks delete mainnet
	brownie networks delete hardhat-fork-curve
	brownie networks delete arbitrum-main
	brownie networks delete arbitrum-fork
	brownie networks delete optimism-main
	brownie networks delete optimism-fork

import_networks:
	brownie networks import brownie-config.yaml

add_frame_networks:
	# https://medium.com/@wormhole_5348/create-a-curve-dao-vote-using-a-ledger-wallet-a55a1825d212
	brownie networks add Ethereum frame host=http://127.0.0.1:1248 chainid=1 explorer=https://api.etherscan.io/api name=Frame

mainnet_reward:
	brownie run scripts/voting/new_vote_stETH-ETH_reward.py simulate --network hardhat-fork-curve

mainnet_real:
	brownie run scripts/voting/new_vote_stETH-ETH_reward.py make_vote --network frame

mainnet_decode:
	brownie run scripts/voting/decode_vote.py --network hardhat-fork-curve

arbitrum_reward:
	brownie run scripts/sidechain/set_wsteth-eth_arbitrum_reward.py simulate --network arbitrum-fork

optimism_reward:
	brownie run scripts/sidechain/set_wsteth-eth_optimism_reward.py simulate --network optimism-fork

mainnet_old_steth_pool:
	brownie run scripts/voting/deploy_staking_reward.py --network hardhat-fork-curve

arbitrum_console:
	brownie console --network arbitrum-fork
