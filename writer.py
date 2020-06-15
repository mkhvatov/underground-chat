import asyncio
from asyncio import CancelledError
import argparse
import logging

from envparse import env


HOST = env.str('HOST', default='minechat.dvmn.org')
PORT = env.int('PORT', default=5050)


parser = argparse.ArgumentParser(description='Underground chat writer client')
parser.add_argument('--debug',
                    action='store_true',
                    default=False,
                    help='activate logging for debug mode',
                    )
parser.add_argument('--host',
                    type=str,
                    default=HOST,
                    help='custom chat host; default=\'minechat.dvmn.org\'',
                    )
parser.add_argument('--port',
                    type=int,
                    default=PORT,
                    help='custom chat port; default=5000',
                    )


async def writer_client(host, port, token, message):
    reader, writer = await asyncio.open_connection(
        host, port)
    logging.info('The connection opened')

    try:
        data = await reader.readline()
        data = data.decode()
        logging.debug(f'sender: {data}')

        writer.write(f'{token}\n'.encode())
        logging.debug(f'writer: send token {token}')

        data = await reader.readline()
        data = data.decode()
        logging.debug(f'sender: {data}')

        data = await reader.readline()
        data = data.decode()
        logging.debug(f'sender: {data}')

        writer.write(f'{message}\n\n'.encode())
        logging.debug(f'writer: {message}')

        data = await reader.readline()
        data = data.decode()
        logging.debug(f'sender: {data}')

    except CancelledError:
        logging.info('Close the connection')
        raise
    except BaseException as error:
        logging.error(f'Error: {error}, {error.__class__}')
    finally:
        writer.close()
        logging.info('The connection closed')


async def main():
    token = 'f261dde6-ae79-11ea-b989-0242ac110002'
    message = 'Hello again!'

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    host = args.host
    port = args.port

    await writer_client(host, port, token, message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        logging.info('Stop the client')
