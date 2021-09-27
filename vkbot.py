from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vkapi import VkRequest
from settings import token
from database.queries import Queries
from database.inserts import Inserts
from buttons import BUTTONS_SEX, BUTTONS_GET_CITY, MAINMENU, EMPTY_KEYBOARD
from datetime import date, datetime
from database.base import DBSession
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def get_data(user_id):
    data = VkRequest().get_userinfo(user_id)
    userinfo = {'user_id': None,
                'age': None,
                'sex': None,
                'city': None,
                'relation': None}

    if 'id' in data['response'][0]:
        userinfo['user_id'] = data['response'][0]['id']

    if 'bdate' in data['response'][0]:
        userinfo['age'] = calculate_age(data['response'][0]['bdate'])
    else:
        write_msg(user_id, f"Введите ваш возраст", EMPTY_KEYBOARD)
        userinfo['age'] = get_age()

    if 'sex' in data['response'][0]:
        userinfo['sex'] = data['response'][0]['sex']
    else:
        write_msg(user_id, f"Введите ваш пол", BUTTONS_SEX)
        userinfo['sex'] = get_sex()

    if 'city' in data['response'][0]:
        userinfo['city'] = data['response'][0]['city']['id']
    else:
        write_msg(user_id, f"Введите ваш город", EMPTY_KEYBOARD)
        userinfo['city'] = get_city()['id']

    if 'relation' in data['response'][0]:
        userinfo['relation'] = data['response'][0]['relation']

    return userinfo


def write_msg(user_id, message, keyboard='', attachment=''):
    vk.method('messages.send', {'user_id': user_id, 'message': message,
                                'random_id': randrange(10 ** 7), 'keyboard': keyboard, 'attachment': attachment})


def send_photos(user_id):
    for match_id in Queries(DBSession).get_matches(user_id):
        message = f'vk.com/id{match_id}'
        vk.method('messages.send', {'user_id': user_id, 'message': message,
                                    'random_id': randrange(10 ** 7)})
        for i in VkRequest().get_photos(match_id):
            attachment = f'photo{match_id}_{i[0]}'
            vk.method('messages.send', {'user_id': user_id,
                                        'random_id': randrange(10 ** 7), 'attachment': attachment})


def start():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text
                write_msg(event.user_id, f"...", MAINMENU)
                if request == "Ввести данные":
                    if not Inserts(DBSession).check_user_exists(event.user_id):
                        userinfo = get_data(event.user_id)
                        Inserts(DBSession).insert_data(userinfo)
                    VkRequest().search_matches(event.user_id)
                    write_msg(event.user_id, f"Успешно", MAINMENU)
                elif request == "Искать":
                    send_photos(event.user_id)


def get_age():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            write_msg(event.user_id, f"Спасибо")
            return event.text


def get_sex():
    mapper = {
        'Мужской': 2,
        'Женский': 1
        }
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            write_msg(event.user_id, f"Спасибо")
            return mapper.get(event.text)


def get_city():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            search_city = VkRequest().search_cities(event.text)
            if search_city is not None:
                write_msg(event.user_id, f"Ваш город {search_city['title']}?", BUTTONS_GET_CITY)
                for response in longpoll.listen():
                    if response.type == VkEventType.MESSAGE_NEW and response.to_me:
                        request = response.text

                        if request == "Да":
                            write_msg(event.user_id, f"Записал")
                            return search_city
                        else:
                            write_msg(event.user_id, f"Тогда введите ваш город еще раз")
                            get_city()
            else:
                write_msg(event.user_id, f"Не нашел такой город, введите ваш город еще раз")


def calculate_age(b_date):
    b_date = datetime.strptime(b_date, '%m.%d.%Y')
    today = date.today()
    return today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day))
