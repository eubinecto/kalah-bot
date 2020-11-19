import asyncio
from typing import Optional

from kalah_python.utils.agent import Agent, Action
import logging
from enum import Enum, auto


class Server:
    class MsgType(Enum):
        START = auto()
        STATE = auto()
        END = auto()

    def __init__(self, agent: Agent):
        self.agent: Agent = agent

    def start_hosting(self, host: str, port: int):
        loop = asyncio.get_event_loop()
        # create task to the
        loop.create_task(asyncio.start_server(self._handle_client,
                                                   host, port))
        logger = logging.getLogger("run")
        try:
            print("running the server forever...")
            loop.run_forever()
        except ValueError as ve:
            logger.error(str(ve))
            loop.close()
        except KeyboardInterrupt as ki:
            logger.error(str(ki))
            loop.close()

    async def _handle_client(self, reader, writer):
        """
        code reference: https://stackoverflow.com/a/48507121
        :param reader:
        :param writer:
        :return:
        """
        msg = None
        while msg != 'quit':
            msg = (await reader.read(255)).decode('utf8')
            action = self._handle_msg(msg)
            if action:
                writer.write(action.to_cmd())
                # clear the buffer
                await writer.drain()
        writer.close()

    def _handle_msg(self, msg: str) -> Optional[Action]:
        msg_type = self.get_msg_type(msg)
        if msg_type == Server.MsgType.START:
            return self._interpret_start_msg(start_msg=msg)
        elif msg_type == Server.MsgType.STATE:
            return self._interpret_state_msg(state_msg=msg)
        elif msg_type == Server.MsgType.END:
            return self._interpret_end_msg(end_msg=msg)
        else:
            raise ValueError("invalid msg type:" + msg_type.name)

    @staticmethod
    def get_msg_type(msg: str) -> MsgType:
        if msg.startswith("START;"):
            return Server.MsgType.START
        if msg.startswith("CHANGE;"):
            return Server.MsgType.STATE
        elif msg.startswith("END\n"):
            return Server.MsgType.END
        else:
            raise ValueError("Invalid msg:" + msg)

    def _interpret_start_msg(self, start_msg: str) -> Optional[Action]:
        """
        e.g.
        START;North
        :param start_msg:
        :return:
        """
        north_or_south = start_msg.split(";")[-1]
        if north_or_south == "North":
            self.agent.new_match_1st()
            # get the next move action
            move_action = self.agent.decide_on_move()
            self.agent.moves()
            return move_action
        elif north_or_south == "South":
            self.agent.new_match_2nd()
            return None  # does not return anything
        else:
            raise ValueError("Invalid start_msg:" + start_msg)

    def _interpret_state_msg(self, state_msg: str):
        """
        e.g.
        CHANGE;1;7,7,7,7,7,7,7,0,0,8,8,8,8,8,8,1;YOU
        :param state_msg:
        :return:
        """
        # TODO: ...
        # update the board.
        # trigger the fsm.
        pass

    def _interpret_end_msg(self, end_msg: str):
        pass
