from typing import Optional
import torch
from kalah_python.utils.ac import ActorCritic
from kalah_python.utils.env import ACKalahEnv
import time
import logging


class Train:

    def __init__(self, ac_kalah_env: ACKalahEnv, ac_model: ActorCritic,
                 logger: logging.Logger, save_path: str):
        self.ac_kalah_env = ac_kalah_env
        self.ac_model = ac_model
        self.h_params = self.ac_kalah_env.h_params
        self.logger = logger
        self.save_path = save_path
        self.optimizer: Optional[torch.optim.Optimizer] = None
        self.run_reward_n: int = 10
        self.run_reward_s: int = 10

    def init_optimizer(self):
        # we use Adam for optimiser
        self.optimizer = torch.optim.Adam(params=self.ac_model.parameters(),
                                          lr=self.h_params.learning_rate)

    def start(self):
        start_time = time.time()
        self.logger.info("h_params: " + str(self.h_params))
        self.logger.info("north_player:{}\nsouth_player:{}"
                          .format(str(self.ac_kalah_env.agent_n),
                                  str(self.ac_kalah_env.agent_s)))
        self.init_optimizer()
        for epi_idx in range(self.h_params.num_episodes):
            # first, reset the env
            self.ac_kalah_env.reset()
            self.ac_kalah_env.play_game()
            episode = self.ac_kalah_env.episode(epi_idx + 1, self.optimizer)
            episode.finish()  # this will update the model. but it doesn't flushes out the reward
            episode.log(start_time, self.logger)

    def save_model(self):
        # after training is done, save the model
        torch.save(self.ac_model.state_dict(), self.save_path)
