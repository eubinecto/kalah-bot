

## Training
### self-play (without policy search)

plots |
--- |
![](.ac_plots_images/ca63e970.png)|

### against `RandomAgent`

plots |
--- |
![](.ac_plots_images/fb55b19d.png)| 
![](.ac_plots_images/ebf78fcf.png)|


---


## debugging the model
so, I've changed:
- layer width: 128 -> 32
- eliminated the shared layer
- don't make any clones

and this is the result: 
![](.ac_plots_images/64a7e050.png)

the win rate increases from 0-500 episodes.
But from that point, it drops.
what if increase the number of layers?

now, let's adopt the rewards from the heuristics here:
![](.ac_plots_images/5d5b9e97.png)