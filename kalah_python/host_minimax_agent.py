from typing import Dict, List
from overrides import overrides
from kalah_python.utils.agent import Agent, Action
from kalah_python.utils.server import Server
from config import HOST, PORT


class MiniMaxAgent(Agent):

    # pseudocode to be discussed
    def chooseMiniMaxMove(NodeClass, gnode, maxDepth=6):
        "Choose bestMove for gnode along w final value"
        if gnode.depth < maxDepth and not gnode.over():
            for move in gnode.moves:
                nxtGnode = NodeClass(gnode.board, gnode.player, gnode.depth + 1)
                nxtGnode.move(move)
                chooseMiniMaxMove(NodeClass, nxtGnode, maxDepth)  # recursion here
                keep = (gnode.next == None)  # 1st of sequence
                if gnode.maximizing():
                    if keep or nxtGnode.value > gnode.value:
                        gnode.value = nxtGnode.value
                        gnode.next = nxtGnode
                        gnode.bestMove = move
                else:
                    if keep or nxtGnode.value < gnode.value:
                        gnode.value = nxtGnode.value
                        gnode.next = nxtGnode
                        gnode.bestMove = move
        return gnode

    @overrides
    def decide_on_action(self, possible_actions: Dict[str, Action]) -> Action:
        """
        :param possible_actions:
        :return:
        """
        print("------decide_on_action----")
        print("It is your turn:")
        print(self.board)
        print("your side:", self.side)
        moves = [*possible_actions.values()]
        action = self.minimax_first_attempt(self, moves)
        print("MiniMax choice: " + str(action))
        return action


def main():
    server = Server(agent=MiniMaxAgent())
    server.start_hosting(host=HOST, port=PORT)


if __name__ == '__main__':
    main()
