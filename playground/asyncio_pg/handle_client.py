import asyncio
import logging
# code reference: https://stackoverflow.com/a/48507121
from config import HOST, PORT


async def handle_client(reader, writer):
    request = None
    while request != 'quit':
        request = (await reader.read(255)).decode('utf8')
        print(request)
        cmd = input("write command here:")
        cmd += "\n"
        writer.write(cmd.encode('utf8'))
        await writer.drain()
    writer.close()


def main():
    logger = logging.getLogger("main")
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.start_server(handle_client, HOST, PORT))
    try:
        print("running the server forever...")
        loop.run_forever()
    except ValueError as ve:
        logger.error(str(ve))
        loop.close()
    except KeyboardInterrupt as ki:
        logger.error(str(ki))
        loop.close()


if __name__ == '__main__':
    main()
