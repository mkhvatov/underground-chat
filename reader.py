import asyncio
from asyncio import CancelledError
import argparse
import datetime

import aiofiles
from envparse import env


HOST = env.str('HOST', default='minechat.dvmn.org')
PORT = env.int('PORT', default=5000)
HISTORY = env.str('HISTORY', default='history.txt')


parser = argparse.ArgumentParser(description='Underground chat reader client')
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
parser.add_argument('--history',
                    type=str,
                    default=HISTORY,
                    help='custom path for history file; default=\'./history.txt\'',
                    )


async def reader_client(host, port, history):
    reader, writer = await asyncio.open_connection(
        host, port)

    try:
        while True:
            data = await reader.readline()
            data = data.decode()
            time = datetime.datetime.now().strftime("[%d.%m.%y %H:%M]")
            message = f'{time} {data}'
            await save_message_to_file(data=message, filename=history)
            print(f'{data}')
    # todo: handle ConnectionResetError
    except CancelledError:
        print('Close the connection')
        raise
    except BaseException as error:
        print(f'Error: {error}, {error.__class__}')
    finally:
        writer.close()


async def save_message_to_file(data, filename):
    async with aiofiles.open(filename, mode='a') as file:
        await file.write(data)


async def main():
    args = parser.parse_args()
    host = args.host
    port = args.port
    history = args.history

    await reader_client(host, port, history)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        print('Stop the client')
