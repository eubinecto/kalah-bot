#
# import argparse
# from dataclasses import dataclass
# import re
# from typing import List, Optional, Generator
# import matplotlib.pyplot as plt
#
# # global vars
# DELIM = "=================================================="
# winner_re = re.compile(r'winner:(.+)\n')
# win_score_re = re.compile(r'win_score:(.*)\n')
# loss_re = re.compile(r'loss:(.*)\n')
# reward_total_re = re.compile(r'reward_total:(.+)\t')
# reward_avg_re = re.compile(r'reward_avg:(.+)\n')
# draw_re = re.compile(r'the game ended in draw')
#
#
# @dataclass
# class LogOpp:
#     draw: bool
#     winner: Optional[str]
#     ac_won: bool
#     win_score: int
#     reward_total: float
#     reward_avg: float
#     loss: float
#
#
# def ext_logs(raws: List[str]) -> List[LogOpp]:
#     logs = list()
#     for raw in raws:
#         draw = True if "draw" in raw else False
#         if not draw:
#             winner = winner_re.findall(raw)[0].strip()
#             win_score = int(win_score_re.findall(raw)[0].strip())
#             ac_won = True if "ac_agent" in winner else False
#         else:
#             winner = None
#             win_score = 0
#             ac_won = False
#         loss = float(loss_re.findall(raw)[0].strip())
#         reward_total = float(reward_total_re.findall(raw)[0].strip())
#         reward_avg = float(reward_avg_re.findall(raw)[0].strip())
#         logs.append(LogOpp(draw, winner, ac_won, win_score, reward_total, reward_avg, loss))
#     return logs
#
#
# def plot(x: List[int], y: List[float], title,
#          x_label, y_label, x_max):
#     plt.plot(x, y)
#     plt.title(title)
#     plt.xlabel(x_label)
#     plt.xlim(0, x_max)
#     plt.show()
#
#
# def get_win_cnts(wins: Generator[int, None, None]) -> Generator[int, None, None]:
#     total = 0
#     for win in wins:
#         if win:
#             total += 1
#         yield total
#
#
# def main():
#     global DELIM
#     parser = argparse.ArgumentParser()
#     parser.add_argument("train_log_path", type=str)
#     args = parser.parse_args()
#     train_log_path = args.train_log_path
#
#     with open(train_log_path, 'r') as fh:
#         text = fh.read()
#
#     raws: List[str] = text.split(DELIM)
#     logs = ext_logs(raws[:-1])  # omit the last one
#
#     episodes = range(1, len(logs) + 1)
#
#     losses = (
#         log.loss
#         for log in logs
#     )
#     episodes_list = list(episodes)
#     # episodes
#     # plot(episodes_list, list(rewards_avgs),
#     #      "average rewards of Actor Critic model (against random agent)",
#     #      "episode", "average reward")
#     plot(episodes_list, list(losses),
#          "losses for each episode",
#          "episode", "loss", len(episodes_list))
#
#
# if __name__ == '__main__':
#     main()
#
