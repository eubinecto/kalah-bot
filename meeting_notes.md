26th of November
---
Do we have enough time?

minimax or RL?
1. all in on minimax
2. or divide it into two teams

trying this out


But should consider the pandemic circumstance.

try with hands-on tutorials.
 - pytorch.

Gain familiarity with libraries.

 
 
##Thoughts on deadlines
- proforma: 26th of November

- Minimax completion: 4th of December (Stefan, Ilia)
- debug & improve by: 11th of December
- presentation: 14th of December (might be on 10-13)
  - won't be able to modify that much 
  - could try changing heuristics <- but have to talk about it in PT
  - something doable in a week.
  - work on this sometime on the weekend.
- project submission: 18th of December, 6pm


## How would we evaluate our bot?
- bash script for evaluation, and record the result. automate it. 
- "grid evaluation"

 
 
## For the next meeting...
TODO.
- deadlines. 
- due tomorrow: proforma: RL Minimax. 
- due next Monday. 


## Resources
Pytorch tutorial - https://torlenor.org/machine%20learning/reinforcement%20learning/2020/10/23/machine_learning_reinforment_learning_kalah_part1.html



---
27th of November

## RL
- from 10am to 1pm (London): Eu-bin & Paul work on first attempt to build A3C. 




---
30th of November

## The size
- the size of the model < 1GB


## The reward function
- borrow heuristics for defining rewards.
- reward = the number of stones in the store.
- reward = stones in the store on my side - ** on opp side. -> discounted. 
  - take into the account the enemy
- winning: very big bonus
- losing: discourage that.
- how others have done it?
- stealing.  : might not need to be a concrete thing.
  - want to steal, therefore I choose (X), the other way around.
  
  
## training
- 1st and 2nd.

## the game engine
- need a virtual environment to simulate the code.
- copy the java code, translate that into python.


## deadline update.
- ~2nd of December: to have something that is reasonably working~
- 3rd of December: we complete the engine in python
- 7th of December: something that is reasonably working (A2C)
- 11th of December: to complete the agent


---
14th of Dec

- the rewards must be non-negative!
- fixed Server & Env. Had many problems when agents swap.
- can train acAgent against itself.
  - it beats MKRefAgent, but not JimmyPlayer
  - possibly due to overfitting
  
 ---
 15th of Dec
- now, make it possible so that you can train AC model against other models
  - against RandomAgent, MinimaxAgent. -> show the gradual increase in win rates (window=10)
- test the resulting agent with JimmyPlayer, MKRefAgent
- train.py
- parsing the logs to get win rate 
- research into the theoretical side of the approach.



--- 

17th of December

## Same problem with
- PyC? -> python compiler Python -> C  (might be Cython).
- PyPi


## reflection on Minimax
- python3 is not fast. The complexity is the same, but the running time is slower than a C++ version.
- translation is impossible
- improvements in complexity? -> we already have alpha-beta pruning (might be incorrect). taking 3 seconds for move.
- If we could speed it up by only changing how it runs in low-level, we could use it.


## Reinforcement Learning
- see if we could swap the rewards with heuristics from minimax.
