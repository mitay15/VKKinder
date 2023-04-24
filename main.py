from vk_api.longpoll import VkEventType, VkLongPoll
from bot import *
from db import *
from config import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id
        if request == 'поиск' or request == 'f':
            bot.get_age_of_user(user_id)
            bot.get_city(user_id)
            bot.looking_for_persons(user_id)
            bot.show_found_person(user_id)
        elif request == 'удалить' or request == 'd':
            delete_table_seen_person()
            create_table_seen_person()
            bot.send_message(user_id, f' База данных очищена! Сейчас наберите "Поиск" или F ')
        elif request == 'смотреть' or request == 'n':
            if bot.get_found_person_id() != 0:
                bot.show_found_person(user_id)
            else:
                bot.send_msg(user_id, f' В начале наберите Поиск или f.  ')
        else:
            bot.send_message(user_id, f'Привет, {bot.name_user(user_id)}! \n Бот готов к поиску, наберите то, что вас интересует: \n '
                                      f' "Поиск или F" - поиск людей. \n'
                                      f' "Удалить или D" - удаляет старую БД и создает новую. \n'
                                      f' "Смотреть или N" - просмотр следующей записи в БД.')