import asyncio
from asyncio import CancelledError
import argparse
import logging
import json

from envparse import env
from dotenv import load_dotenv, set_key, find_dotenv


def get_args():
    host = env.str('SERVER_HOST', default='minechat.dvmn.org')
    port = env.int('SERVER_WRITE_PORT')
    token = env.str('TOKEN', default=None)
    username = env.str('USERNAME', default=None)
    message = env.str('MESSAGE', default='Hello everyone!')

    parser = argparse.ArgumentParser(description='Underground chat writer client')
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='activate logging for debug mode',
                        )
    parser.add_argument('--host',
                        type=str,
                        default=host,
                        help='server host; default=\'minechat.dvmn.org\'',
                        )
    parser.add_argument('--port',
                        type=int,
                        default=port,
                        help='server write port; default=5050',
                        )
    parser.add_argument('--token',
                        type=str,
                        default=token,
                        help='token for authorization; default=None',
                        )
    parser.add_argument('--username',
                        type=str,
                        default=username,
                        help='username for registration',
                        )
    parser.add_argument('--message',
                        type=str,
                        default=message,
                        help='message to send',
                        )
    return parser.parse_args()


def sanitize(message):
    return message.replace('\n', '')


async def connect(host, port):
    reader, writer = await asyncio.open_connection(
        host, port)
    logging.debug('The connection opened')

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')

    return reader, writer


async def register(reader, writer, username):
    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')

    if username:
        username = sanitize(username)
        writer.write(f'{username}\n'.encode())
        logging.debug(f'writer: send username {username}')
    else:
        writer.write('\n'.encode())

    data = await reader.readline()
    data = data.decode()
    data = json.loads(data)
    logging.debug(f'sender: {data}')
    token = data['account_hash']
    nickname = data['nickname']
    logging.debug(f'registered as: {nickname}')

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')
    return token


async def authorize(reader, writer, token):
    if not token:
        writer.write('\n'.encode())
        logging.debug(f'writer: send empty string')
        return False

    writer.write(f'{token}\n'.encode())
    logging.debug(f'writer: send token {token}')

    data = await reader.readline()
    data = data.decode()
    data = json.loads(data)
    logging.debug(f'sender: {data}')
    if not data:
        logging.debug('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        return False

    nickname = data['nickname']
    logging.debug(f'authorized as: {nickname}')

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')
    return True


async def submit_message(reader, writer, message):
    message = sanitize(message)
    writer.write(f'{message}\n\n'.encode())
    logging.debug(f'writer: {message}')

    data = await reader.readline()
    data = data.decode()
    logging.debug(f'sender: {data}')


async def writer_client(host, port, token, message, username):
    reader, writer = await connect(host, port)

    try:
        authorized = await authorize(reader, writer, token)

        if not authorized:
            token = await register(reader, writer, username)
            set_key(find_dotenv(), "TOKEN", token)

            writer.close()
            logging.debug('The connection closed')

            reader, writer = await connect(host, port)

            await authorize(reader, writer, token)

        await submit_message(reader, writer, message)

    # todo:
    except CancelledError:
        logging.debug('Close the connection')
        raise
    except BaseException as error:
        logging.error(f'Error: {error}, {error.__class__}')
    finally:
        writer.close()
        logging.debug('The connection closed')


async def main():
    load_dotenv()
    args = get_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    host = args.host
    port = args.port
    token = args.token
    username = args.username
    message = args.message

    await writer_client(host, port, token, message, username)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.close()
    except KeyboardInterrupt:
        logging.debug('Stop the client')
