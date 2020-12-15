import argparse
from dataclasses import dataclass
import re
from typing import List
import matplotlib.pyplot as plt

# global vars
DELIM = "=================================================="
win_score_re = re.compile(r'win_score:(.*)\n')
reward_n_total_re = re.compile(r'NORTH	reward_total:(.+)\t')
reward_s_total_re = re.compile(r'SOUTH	reward_total:(.+)\t')
reward_n_avg_re = re.compile(r'NORTH.*reward_avg:(.+)\n')
reward_s_avg_re = re.compile(r'SOUTH.*reward_avg:(.+)\n')


@dataclass
class LogSelf:
    draw: bool
    win_score: int
    reward_n_total: float
    reward_n_avg: float
    reward_s_total: float
    reward_s_avg: float


def ext_self_logs(raws: List[str]) -> List[LogSelf]:
    logs = list()
    for raw in raws:
        draw = True if "draw" in raw else False
        if not draw:
            win_score = int(win_score_re.findall(raw)[0].strip())
        else:
            win_score = 0
        reward_n_total = float(reward_n_total_re.findall(raw)[0].strip())
        reward_s_total = float(reward_s_total_re.findall(raw)[0].strip())
        reward_n_avg = float(reward_n_avg_re.findall(raw)[0].strip())
        reward_s_avg = float(reward_s_avg_re.findall(raw)[0].strip())
        logs.append(LogSelf(draw, win_score,
                            reward_n_total, reward_n_avg,
                            reward_s_total, reward_s_avg))
    return logs


def plot(x: List[int], y: List[float], title: str):
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel("episode")
    plt.ylabel("average reward")
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
    self_logs = ext_self_logs(raws[:-1])  # omit the last one

    # plot the average rewards
    reward_n_avgs = (
        self_log.reward_n_avg
        for self_log in self_logs
    )
    reward_s_avgs = (
        self_log.reward_s_avg
        for self_log in self_logs
    )

    # episodes
    episodes = list(range(1, len(self_logs) + 1))
    plot(episodes, list(reward_n_avgs), "average rewards of north agent (self-play)")
    plot(episodes, list(reward_s_avgs), "average rewards of south agent (self-play)")


if __name__ == '__main__':
    main()
