import asyncio
from asyncio import CancelledError
import argparse
import logging
import json

from envparse import env


HOST = env.str('HOST', default='minechat.dvmn.org')
PORT = env.int('PORT', default=5050)
TOKEN = env.str('TOKEN', default=None)


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
parser.add_argument('--token',
                    type=str,
                    default=TOKEN,
                    help='token for authorization; default=None',
                    )


async def connect(host, port):
    reader, writer = await asyncio.open_connection(
        host, port)
    logging.info('The connection opened')

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')

    return reader, writer


async def register(reader, writer, nickname=None):
    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')

    if nickname:
        writer.write(f'{nickname}\n'.encode())
        logging.debug(f'writer: send nickname {nickname}')
    else:
        writer.write('\n'.encode())

    data = await reader.readline()
    data = data.decode()
    data = json.loads(data)
    logging.debug(f'sender: {data}')
    token = data['account_hash']

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')
    return token


async def authorize(reader, writer, token: str) -> bool:
    writer.write(f'{token}\n'.encode())
    logging.debug(f'writer: send token {token}')

    data = await reader.readline()
    data = data.decode()
    data = json.loads(data)
    logging.debug(f'sender: {data}')
    if not data:
        logging.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        return False

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')
    return True


async def submit_message(reader, writer, message):
    writer.write(f'{message}\n\n'.encode())
    logging.debug(f'writer: {message}')

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')


async def writer_client(host, port, token, message, nickname):
    reader, writer = await connect(host, port)

    authorized = False
    if token:
        authorized = await authorize(reader, writer, token)

    if not token or not authorized:
        token = await register(reader, writer, nickname)
        writer.close()
        logging.info('The connection closed')

        reader, writer = await connect(host, port)

        await authorize(reader, writer, token)

    try:
        await submit_message(reader, writer, message)

    except CancelledError:
        logging.info('Close the connection')
        raise
    except BaseException as error:
        logging.error(f'Error: {error}, {error.__class__}')
    finally:
        writer.close()
        logging.info('The connection closed')


async def main():
    message = 'Hello again!'

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    host = args.host
    port = args.port
    # token = args.token
    # token = 'f261dde6-ae79-11ea-b989-0242ac110002'
    token = 'f261dde6-ae79-11ea-b989-0242ac110001'
    nickname = 'Ivan'
    nickname = None

    await writer_client(host, port, token, message, nickname)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        logging.info('Stop the client')
