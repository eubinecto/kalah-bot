from typing import Dict
from overrides import overrides
from kalah_python.utils.agent import Agent, Action
from kalah_python.utils.server import Server
from config import HOST, PORT


class A2CAgent(Agent):

    @overrides
    def decide_on_action(self, possible_actions: Dict[str, Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        # load the pretrained model from data. (<1GB)
        model = ...
        action = model(self.board)
        return action


def main():
    server = Server(agent=A2CAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
