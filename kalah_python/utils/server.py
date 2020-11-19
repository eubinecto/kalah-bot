import asyncio
from kalah_python.utils.agent import Agent
from config import HOST, PORT
import logging


class Protocol:
    BUFF_SIZE: int = 100

    def interpret_state_msg(self, state_msg: str):
        # update the board
        pass


class Server:

    def __init__(self, agent: Agent,
                 host: str = HOST, port: int = PORT):
        self.agent: Agent = agent
        self.loop = asyncio.get_event_loop()
        # create task to the
        self.loop.create_task(asyncio.start_server(self.handle_client,
                                                   HOST, PORT))

    async def handle_client(self, reader, writer):
        """
        code reference: https://stackoverflow.com/a/48507121
        :param reader:
        :param writer:
        :return:
        """
        request = None
        while request != 'quit':
            request = (await reader.read(255)).decode('utf8')
            cmd = ...
            writer.write(cmd.encode('utf8'))
            # clear the buffer
            await writer.drain()
        writer.close()

    def run(self):
        logger = logging.getLogger("run")
        try:
            print("running the server forever...")
            self.loop.run_forever()
        except ValueError as ve:
            logger.error(str(ve))
            self.loop.close()
        except KeyboardInterrupt as ki:
            logger.error(str(ki))
            self.loop.close()


