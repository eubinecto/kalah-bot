import argparse
from dataclasses import dataclass
import re
from typing import List, Optional
import matplotlib.pyplot as plt

# global vars
DELIM = "=================================================="
win_score_re = re.compile(r'win_score:(.*)\n')
reward_n_total_re = re.compile(r'reward_total:(.+)\t')
reward_n_avg_re = re.compile(r'reward_avg:(.+)\n')
reward_s_total_re = re.compile(r'reward_total:(.+)\t')
reward_s_avg_re = re.compile(r'reward_avg:(.+)\n')
draw_re = re.compile(r'the game ended in draw')


@dataclass
class LogSelf:
    draw: bool
    win_score: int
    reward_n_total: float
    reward_n_avg: float
    reward_s_total: float
    reward_n_avg: float


def ext_logs(raws: List[str]) -> List[LogSelf]:
    logs = list()
    for raw in raws:
        draw = True if "draw" in raw else False
        if not draw:
            win_score = int(win_score_re.findall(raw)[0].strip())
        else:
            win_score = 0
            ac_won = False
        reward_total = float(reward_total_re.findall(raw)[0].strip())
        reward_avg = float(reward_avg_re.findall(raw)[0].strip())
        logs.append(LogSelf(draw, winner, ac_won, win_score, reward_total, reward_avg))
    return logs


def plot(x: List[int], y: List[float]):
    plt.bar(x, y)
    plt.show()


def main():
    global DELIM
    parser = argparse.ArgumentParser()
    parser.add_argument("train_log_path", type=str)
    args = parser.parse_args()
    train_log_path = args.train_log_path

    with open(train_log_path, 'r') as fh:
        text = fh.read()

    raws: List[str] = text.split(DELIM)
    logs = ext_logs(raws[:-1])  # omit the last one

    # plot the average rewards
    rewards_avgs = (
        log.reward_avg
        for log in logs
    )
    # episodes
    episodes = list(range(1, len(logs) + 1))
    plot(episodes, list(rewards_avgs))


if __name__ == '__main__':
    main()

