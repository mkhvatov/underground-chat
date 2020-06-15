import asyncio
from asyncio import CancelledError
import argparse
import datetime

from envparse import env


HOST = env.str('HOST', default='minechat.dvmn.org')
PORT = env.int('PORT', default=5050)


parser = argparse.ArgumentParser(description='Underground chat writer client')
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

    try:
        data = await reader.readline()
        data = data.decode()
        print(f'{data}')

        writer.write(f'{token}\n'.encode())

        data = await reader.readline()
        data = data.decode()
        print(f'{data}')

        writer.write(f'{message}\n\n'.encode())

    except CancelledError:
        print('Close the connection')
        raise
    except BaseException as error:
        print(f'Error: {error}, {error.__class__}')
    finally:
        writer.close()


async def main():
    token = 'f261dde6-ae79-11ea-b989-0242ac110002'
    message = 'Hello again!'

    args = parser.parse_args()
    host = args.host
    port = args.port

    await writer_client(host, port, token, message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        print('Stop the client')
