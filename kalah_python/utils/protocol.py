
from enum import Enum, auto


class MsgType(Enum):
    START = auto()
    STATE = auto()
    END = auto()


class Protocol:
    @staticmethod
    def get_msg_type(msg: str) -> MsgType:
        if msg.startswith("START;"):
            return MsgType.START
        if msg.startswith("CHANGE;"):
            return MsgType.STATE
        elif msg.startswith("END\n"):
            return MsgType.END
        else:
            raise ValueError("Invalid msg:" + msg)

    @staticmethod
    def interpret_start_msg(start_msg: str):
        """
        e.g.
        START;North
        :param start_msg:
        :return:
        """
        pass

    @staticmethod
    def interpret_state_msg(state_msg: str):
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


