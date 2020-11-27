# Group 25 proforma
- date: 27th of November 2020
- authors
  - Stefan Ciocate
  - Eu-Bin Kim
  - Paul Stefanescu
  - Ilia Plavnik
  
## Approach
### Reinforcement Learning
- try out A3C (Async advantage actor critic)
- for the framework: Pytorch or Tensorflow
- reference tutorial: [Tackling the game Kalah using reinforcement learning - Part 1](https://torlenor.org/machine%20learning/reinforcement%20learning/2020/10/23/machine_learning_reinforment_learning_kalah_part1.html)
- have it play kalah against: itself, `RefAgent`, `Jimmy Player`
- deadlines
  - 2nd of December: to have something that is reasonably working
  - 11th of December: to complete the agent
 
 
### Minimax
- experiment with `RandomAgent`, `JimmyPlayer`.
- the goal is to outperform `JimmyPlayer` by a win rate of over 50%. 
- heuristics from [*from Searching and Game Playing:
An Artificial Intelligence Approach to Mancala*](https://fiasco.ittc.ku.edu/publications/documents/Gifford_ITTC-FY2009-TR-03050-03.pdf):
  - H0: First valid move (furthest valid bin from my home)
  - H1: How far ahead of my opponent I am
  - H2: How close I am to winning (> half)
  - H3: How close opponent is to winning (> half)
  - H4: Number of stones close to my home
  - H5: Number of stones far away from my home
  - H6: Number of stones in middle of board (neither close nor far from home)
- Define specialise methods for the heuristics above, pick the best performing one.
- deadlines
  - 4th of December: to have something that is reasonably working
  - 11th of December: to complete the agent


### Minimax vs. RL
- 12th ~ 13th of December: choose one of them, make presentation
- 14th of December: present (submit) presentation on the chosen algorithm
- Until the 18th of December: try as much as we can to improve it.



## How we split the work
- RL: Eu-Bin, Paul
- Minimax: Stefan, Ilia
- pair programming: make use of `Code with Me` or `CodeTogether` plugin of `Pycharm`.


