## StakingRewards

**CurveLiquidityFarmingManager.vy**

Old CurveLiquidityFarmingManager Contract used by the last LDO reward season:

https://etherscan.io/address/0x0db86d2d8707f260d455f63790f5f5e5d828a961#code

**CurveLiquidityFarmingManager.sol.deployed**  

CurveLiquidityFarmingManager used now for wstETH

Code deploy by Lido at https://etherscan.io/address/0x4f48031b0ef8accea3052af00a3279fba31b50d8#code


**CurveLiquidityFarmingManager.sol.deployed.diff**

Shows the diff between the two contract

```
1c1
< # @version 0.2.8
---
> # @version 0.3.9
6a7
> # Code deploy by Lido at https://etherscan.io/address/0x9d81153ae611aeb53e5f137b701c67c2ebffcdae
15c16
< ldo_token: constant(address) = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32
---
> wsteth_token: constant(address) = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0
61c62
<         distributing `ldo_token.balanceOf(self)` tokens throughout the period. The current
---
>         distributing `wsteth_token.balanceOf(self)` tokens throughout the period. The current
65c66
<     amount: uint256 = ERC20(ldo_token).balanceOf(self)
---
>     amount: uint256 = ERC20(wsteth_token).balanceOf(self)
70c71
<     ERC20(ldo_token).approve(rewards, amount)
---
>     ERC20(wsteth_token).approve(rewards, amount)
```


## StakingRewards

**StakingRewards.sol**

Old StakingRewards Contract used by the LDO reward season:

https://etherscan.io/address/0x99ac10631f69c753ddb595d074422a0922d9056b#code


**StakingRewards.sol.deployed**  

Code used now for wstETH

Code deploy by Lido at https://etherscan.io/address/0x4f48031b0ef8accea3052af00a3279fba31b50d8#code


**StakingRewards.sol.deployed.diff**

Shows the diff between the two contracts

```
1a2,5
>  *Submitted for verification at Etherscan.io on 2023-09-18
> */
> 
> /**
4a9,11
> // Code deploy by Lido at https://etherscan.io/address/0x4f48031b0ef8accea3052af00a3279fba31b50d8
>  
>  
```
