import asyncio
from kalah_python.utils.agent import Agent
from enum import Enum, auto
import logging
from sys import stdout
logging.basicConfig(stream=stdout, level=logging.INFO)
# suppress logs from transitions
transitions_logger = logging.getLogger("transitions.core")
transitions_logger.setLevel(logging.WARN)


class Server:
    class MsgType(Enum):
        START = auto()
        STATE = auto()
        END = auto()

    def __init__(self, agent: Agent):
        self.agent: Agent = agent

    @staticmethod
    def get_msg_type(msg: str) -> MsgType:
        print(msg)
        if msg.startswith("START;"):
            return Server.MsgType.START
        if msg.startswith("CHANGE;"):
            return Server.MsgType.STATE
        elif msg == "END":
            return Server.MsgType.END
        else:
            raise ValueError("Invalid msg:" + msg)

    def start_hosting(self, host: str, port: int):
        loop = asyncio.get_event_loop()
        # create task to the
        loop.create_task(asyncio.start_server(self._handle_client,
                                              host, port))
        logger = logging.getLogger("run")
        try:
            logger.info("running the server...")
            loop.run_forever()
        except Exception as ve:
            logger.error(str(ve))
            loop.stop()
            loop.close()

    async def _handle_client(self, reader, writer):
        """
        code reference: https://stackoverflow.com/a/48507121
        :param reader:
        :param writer:
        :return:
        """
        logger = logging.getLogger("_handle_client")
        # TODO: rather than doing this, there better be two handlers
        # one is just interpreting the message
        # the other is for sending messages to the engine.
        # and they should run concurrently.
        # okay. so what's the problem?
        # one has to constantly listen to the client <- must not be interrupted.
        # while at the same time, the other has to send something to client.
        msg = None
        while msg != 'quit':
            msg = (await reader.read(255)).decode('utf8')
            logger.debug(msg)
            self._handle_msg(msg.strip())
            if self.agent.action_is_registered():  # check if an action is registered.
                try:
                    # this will fail if the connection is lost
                    writer.write(self.agent.action.to_cmd())
                except ConnectionResetError as cre:
                    self.agent.game_over()
                    raise cre
                else:
                    # if the command was successful, commit and unregister the action
                    # commit the action
                    self.agent.commit_action()
                    self.agent.unregister_action()
                    # clear the buffer
                    await writer.drain()
        writer.close()

    def _handle_msg(self, msg: str):
        msg_type = self.get_msg_type(msg)
        if msg_type == Server.MsgType.START:
            self._interpret_start_msg(start_msg=msg)
        elif msg_type == Server.MsgType.STATE:
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
        north_or_south = start_msg.split(";")[-1]
        if north_or_south == "North":
            # start the match as a 1st player
            self.agent.new_match_2nd()
        elif north_or_south == "South":
            # start the match as a 2nd player
            self.agent.new_match_1st()
        else:
            raise ValueError("Invalid start_msg:" + start_msg)

    def _interpret_change_msg(self, change_msg: str):
        """
        e.g.
        CHANGE;1;7,7,7,7,7,7,7,0,0,8,8,8,8,8,8,1;YOU
        CHANGE;3;8,8,7,7,7,7,7,0,7,7,0,8,8,8,8,1;OPP
        :param change_msg:
        :return:
        """
        # update the board before raising triggers
        self.agent.board.update_board(change_msg)
        game_state = change_msg.split(";")[-1]
        if game_state == "YOU":
            self.agent.game_state_is_you()
        elif game_state == "OPP":
            self.agent.game_state_is_opp()
        elif game_state == "END":
            self.agent.game_state_is_end()
        else:
            raise ValueError("invalid game_state:" + str(game_state))

    def _interpret_end_msg(self):
        print("game is finished")
        print("your score:", self.agent.board.get_store(self.agent.side))
        print("opponent's score:", self.agent.board.get_store(self.agent.side.opposite()))
