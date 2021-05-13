# Функции сервера:
#     - принимает сообщение клиента;
#     - формирует ответ клиенту;
#     - отправляет ответ клиенту;
#     - имеет параметры командной строки:
#         * -p <port> — TCP-порт для работы (по умолчанию использует 7777);
#         * -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import time
import pickle
import logging
import log.server_log_config

# Для проведения теста функций установить значение переменной my_test = True
my_test = False

logger = logging.getLogger('my_server')

s = socket(AF_INET, SOCK_STREAM)
s.bind(('', 8007))
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.listen(5)

logger.info('server starts')
timestamp = int(time.time())

users = {
    'KonTroAll': 'SpaceShip007',
}

usernames_friends = ['Julia']
room_names = ['#smalltalk']

dict_signals = {
    100: 'welcome!',
    101: 'do not come here!',
    200: 'OOK!',
    201: 'created',
    202: 'accepted',
    400: 'неправильный запрос/JSON-объект',
    401: 'не авторизован',
    402: 'неправильный логин/пароль',
    403: 'пользователь заблокирован',
    404: 'пользователь/чат отсутствует на сервере',
    409: 'уже имеется подключение с указанным логином',
    410: 'адресат существует, но недоступен (offline)',
    500: 'ошибка сервера'
}

authenticate = True
presence = True
user_user = True
user_all = True

try:
    while True:
        if my_test:
            break

        client, addr = s.accept()

        # вход на сервер
        logger.info('start connection with user')
        dict_welcome = {
            'action': 'join',
            'response': 100,
            'alert': dict_signals[100]
        }
        client.send(pickle.dumps(dict_welcome))

        # Авторизация пользователя на сервере
        if authenticate:
            logger.info('start user_authenticate')
            data = client.recv(1024)
            client_data = pickle.loads(data)

            if client_data['action'] == 'authenticate' and presence == False:
                user = client_data['user']
                for us, pas in users.items():
                    for val in user.values():
                        if us == val and pas == user['password']:
                            dict_auth_response = {
                                'response': 200,
                                'alert': dict_signals[200]
                            }
                            print('authenticate completed!')
                            client.send(pickle.dumps(dict_auth_response))
                            presence = True
                            logger.info('authentication complete')
                            break
                        else:
                            dict_auth_response = {
                                'response': 402,
                                'error': dict_signals[402]
                            }
                            print('error!')
                            client.send(pickle.dumps(dict_auth_response))
                            logger.info('authentication failed')
                            break
            else:
                dict_auth_response = {
                    'response': 409,
                    'error': dict_signals[409]
                }
                print('Someone is already connected with the given user name!')
                presence = True
                signal_409 = True
                client.send(pickle.dumps(dict_auth_response))
                logger.info('Someone is already connected with the given user name!')


        # Проверка присутствия пользователя
        def presence_user():
            logger.info('start user_presence')
            dict_probe = {
                'action': 'probe',
                'time': timestamp
            }
            client.send(pickle.dumps(dict_probe))
            presence_data = client.recv(1024)
            print('Сообщение от клиента: ', pickle.loads(presence_data), ', длиной ', len(presence_data), ' байт')
            logger.info('get data from user')
            return pickle.loads(presence_data)['action']


        if presence:
            presence_user()

        # Отправка сообщения другому пользователю
        if user_user:
            if authenticate:
                logger.info('start message_to_user')
                msg_data = pickle.loads(client.recv(1024))
                if msg_data['action'] == 'msg':
                    if list(msg_data['to'])[0].isalpha():
                        for i in usernames_friends:
                            if msg_data['to'] == i:
                                msg_dict = {
                                    'response': 200,
                                    'time': timestamp,
                                    'alert': dict_signals[200]
                                }
                                client.send(pickle.dumps(msg_dict))
                                logger.info('message send')
                            else:
                                msg_dict = {
                                    'response': 404,
                                    'time': timestamp,
                                    'alert': dict_signals[404]
                                }
                                client.send(pickle.dumps(msg_dict))
                                logger.info('пользователь/чат отсутствует на сервере')
            else:
                msg_data = pickle.loads(client.recv(1024))
                dict_not_auth = {
                    'response': 401,
                    'alert': dict_signals[401]
                }
                client.send(pickle.dumps(dict_not_auth))
                logger.info('неавторизованный пользователь отправил сообщение')

        # Отправка сообщения в чат
        if user_all:
            if authenticate:
                logger.info('start message_to_all')
                msg_for_room_data = pickle.loads(client.recv(1024))
                if msg_for_room_data['action'] == 'msg':
                    for i in room_names:
                        if i == msg_for_room_data['to']:
                            room_dict = {
                                'response': 200,
                                'time': timestamp,
                                'alert': dict_signals[200]
                            }
                            client.send(pickle.dumps(room_dict))
                            logger.info('message send')
                        else:
                            room_dict = {
                                'response': 404,
                                'time': timestamp,
                                'alert': dict_signals[404]
                            }
                            client.send(pickle.dumps(room_dict))
                            logger.info('пользователь/чат отсутствует на сервере')
            else:
                msg_for_room_data = pickle.loads(client.recv(1024))
                dict_not_auth = {
                    'response': 401,
                    'alert': dict_signals[401]
                }
                client.send(pickle.dumps(dict_not_auth))
                logger.info('неавторизованный пользователь отправил сообщение')

        # logout
        if authenticate:
            print(pickle.loads(client.recv(1024)))
            logger.info('logout from server')

        # отключение от сервера
        client.send(pickle.dumps({'action': 'quit'}))
        logger.info('server quit')

        client.close()
except Exception as e:
    logger.critical(e)

# оптимизированные для проведения тестов функции, написанные выше
if my_test:
    authenticate = False

    dict_auth = {
        'action': 'authenticate',
        'time': timestamp,
        'user': {
            'user_name': 'KonTroAll',
            'password': 'SpaceShip007'
        }
    }


    def authenticate_user(my_dict):
        client_data = my_dict

        if client_data['action'] == 'authenticate':
            user = client_data['user']
            for us, pas in users.items():
                for val in user.values():
                    if us == val and pas == user['password']:
                        dict_auth_response = {
                            'response': 200,
                            'alert': dict_signals[200]
                        }
                        return 'authenticate completed!'
                    else:
                        dict_auth_response = {
                            'response': 402,
                            'error': dict_signals[402]
                        }
                        return 'error!'
        else:
            dict_auth_response = {
                'response': 409,
                'error': dict_signals[409]
            }
            return 'Someone is already connected with the given user name!'


    # Проверка присутствия пользователя
    def presence_user(my_dict):
        dict_probe = {
            'action': 'probe',
            'time': timestamp
        }
        presence_data = my_dict
        return presence_data['action']


    # Отправка сообщения другому пользователю
    def message_to_user(my_dict):
        msg_data = my_dict
        if authenticate_user(dict_auth) == 'authenticate completed!':
            if msg_data['action'] == 'msg':
                if list(msg_data['to'])[0].isalpha():
                    for i in usernames_friends:
                        if msg_data['to'] == i:
                            msg_dict = {
                                'response': 200,
                                'time': timestamp,
                                'alert': dict_signals[200]
                            }
                            return 'OOK!'
                        else:
                            msg_dict = {
                                'response': 404,
                                'time': timestamp,
                                'alert': dict_signals[404]
                            }
                            return 'пользователь/чат отсутствует на сервере'
        else:
            msg_data = my_dict
            dict_not_auth = {
                'response': 401,
                'alert': dict_signals[401]
            }
            return 'не авторизован'


    #
    #     # Отправка сообщения в чат
    def message_to_all(my_dict):
        if authenticate_user(dict_auth) == 'authenticate completed!':
            msg_for_room_data = my_dict
            if msg_for_room_data['action'] == 'msg':
                for i in room_names:
                    if i == msg_for_room_data['to']:
                        room_dict = {
                            'response': 200,
                            'time': timestamp,
                            'alert': dict_signals[200]
                        }
                        return 'OOK!'
                    else:
                        room_dict = {
                            'response': 404,
                            'time': timestamp,
                            'alert': dict_signals[404]
                        }
                        return 'пользователь/чат отсутствует на сервере'
        else:
            msg_for_room_data = my_dict
            dict_not_auth = {
                'response': 401,
                'alert': dict_signals[401]
            }
            return 'не авторизован'
