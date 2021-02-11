import asyncio
from kalah_python.utils.agents import Agent
from enum import Enum, auto
import logging
from sys import stdout

from kalah_python.utils.enums import AgentState

logging.basicConfig(stream=stdout, level=logging.INFO)
# suppress logs from transitions
transitions_logger = logging.getLogger("transitions.core")
transitions_logger.setLevel(logging.INFO)


class Server:
    class MsgType(Enum):
        START = auto()
        CHANGE = auto()
        END = auto()

    def __init__(self, agent: Agent, listen_forever: bool):
        self.agent: Agent = agent
        print("---------listen_forever:" + str(listen_forever))
        self.listen_forever = listen_forever

    @staticmethod
    def get_msg_type(msg: str) -> MsgType:
        logger = logging.getLogger("get_msg_type")
        logger.info(msg)
        if msg.startswith("START;"):
            return Server.MsgType.START
        if msg.startswith("CHANGE;"):
            return Server.MsgType.CHANGE
        elif msg == "END":
            return Server.MsgType.END
        else:
            raise ValueError("Invalid msg:" + msg)

    def start_hosting(self, host: str, port: int):
        logger = logging.getLogger("run")
        loop = asyncio.get_event_loop()
        # create task to the
        loop.create_task(asyncio.start_server(self._handle_client, host, port))
        logger.info("running the server...")
        # exception handling
        loop.set_exception_handler(self.handle_exception)
        loop.run_forever()

    def handle_exception(self, loop, context):
        print(context['exception'])
        if self.listen_forever:
            print("listening forever")
            self.reset_states()
        else:
            print("stop listening")
            loop.stop()  # stop the loop on any exception.

    async def _handle_client(self, reader, writer):
        """
        code reference: https://stackoverflow.com/a/48507121
        :param reader:
        :param writer:
        :return:
        """
        logger = logging.getLogger("_handle_client")
        msg = None
        while msg != "END":  # while msg is not empty string
            msg = (await reader.read(255)).decode('utf8').strip()
            if not msg:
                raise ConnectionResetError
            logger.info(msg)
            for msg_split in msg.split("\n"):
                if msg_split:
                    self._interpret_msg(msg.strip())
            if self.agent.action_is_registered():  # check if an action is registered.
                try:
                    # make a move on the server side.
                    # this will fail if the connection is lost
                    writer.write(self.agent.action.to_cmd())
                except ConnectionResetError as cre:
                    raise cre
                else:
                    # if the command was successful, commit and unregister the action
                    # commit the action
                    self.agent.commit_action()
                    self.agent.unregister_action()
                    # clear the buffer
                    await writer.drain()
        writer.close()

    def _interpret_msg(self, msg: str):
        msg_type = self.get_msg_type(msg)
        if msg_type == Server.MsgType.START:
            self._interpret_start_msg(start_msg=msg)
        elif msg_type == Server.MsgType.CHANGE:
            self._interpret_change_msg(change_msg=msg)
        elif msg_type == Server.MsgType.END:
            self._interpret_end_msg()
        else:
            raise ValueError("invalid msg type:" + msg_type.name)

    def _interpret_start_msg(self, start_msg: str):
        """
        e.g.
        START;North
        :param start_msg:
        :return:
        """
        # parse the message to find out which side of the board
        # the agent should start playing the game from.
        north_or_south = start_msg.split(";")[-1].strip()
        if "North" in north_or_south:
            # start the match as a 1st player
            self.agent.new_match_2nd()
        elif "South" in north_or_south:
            # start the match as a 2nd player
            self.agent.new_match_1st()
        else:
            raise ValueError("Invalid start_msg:" + start_msg)

    def _interpret_change_msg(self, change_msg: str):
        """
        e.g.
        CHANGE;1;7,7,7,7,7,7,7,0,0,8,8,8,8,8,8,1;YOU
        CHANGE;3;8,8,7,7,7,7,7,0,7,7,0,8,8,8,8,1;OPP
        and for swap:
        CHANGE;SWAP;8,8,8,8,8,8,7,0,7,7,7,7,7,7,0,1;YOU
        :param change_msg:
        :return:
        """
        logger = logging.getLogger("_interpret_change_msg")
        # update the board before raising triggers
        self.agent.board.update_board(change_msg)
        game_state = change_msg.strip().split(";")[-1]
        logger.info(game_state)
        if self.agent.state == AgentState.WAIT_FOR_SWAP_DECISION:
            if change_msg.strip().split(";")[1] == "SWAP":
                self.agent.opp_swap()
            else:
                self.agent.opp_no_swap()
                self.agent.game_state_is_you()
        else:
            if game_state == "YOU":
                self.agent.game_state_is_you()
            elif game_state == "OPP":
                self.agent.game_state_is_opp()
            elif game_state in ("END\nEND" or "END"):  # non-deterministic
                self.agent.game_state_is_end()
            else:
                raise ValueError("invalid game_state:" + game_state)

    def _interpret_end_msg(self):
        print("------game is finished--------")
        print("your score:", self.agent.board.store(self.agent.side))
        print("opponent's score:", self.agent.board.store(self.agent.side.opposite()))
        raise ConnectionResetError

    def reset_states(self):
        self.agent.reset()
        self.agent.board.reset()
