from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
from datetime import date
import vk_api
from config import access_token, community_token
from random import randrange
from pprint import pprint
from db import *


# import psycopg2
# from psycopg2 import errors


class Bot:
    def __init__(self):
        print('Bot was created')
        self.vk_user = vk_api.VkApi(token=access_token)
        self.vk_user_got_api = self.vk_user.get_api()
        self.vk_group = vk_api.VkApi(token=community_token)
        self.vk_group_got_api = self.vk_group.get_api()
        self.longpoll = VkLongPoll(self.vk_group)

    def send_message(self, user_id, message):
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=randrange(10 ** 7)
        )

    def name_user(self, user_id):
        user_info = self.vk_group_got_api.users.get(user_id=user_id)
        # print(user_info)
        try:
            name = user_info[0]['first_name']
            return name
        except KeyError:
            self.send_message(user_id, "Ошибка")

    def name_of_years(self, years):
        age = int(years)
        if age % 10 == 1:
            return f'{age} год'
        elif age % 10 > 1 and age % 10 < 5:
            return f'{age} года'
        elif age % 10 == 0 or age % 10 > 4 or age % 100 > 10 and age % 100 < 20:
            return f'{age} лет'


    def input_age(self, user_id, age):
        global age_from, age_to
        age_from_to = age.split("-")
        try:
            age_from = int(age_from_to[0])
            age_to = int(age_from_to[1])
            if age_from == age_to:
                self.send_message(user_id, f'Найдем пользователей, которым {self.name_of_years(age_to)}')
                return
            self.send_message(user_id, f'Найдем пользователей, возраст которых в пределах от {self.name_of_years(age_from)} и до {self.name_of_years(age_to)}')
            return
        except IndexError:
            age_to = int(age)
            self.send_message(user_id, f'Найдем пользователей, которым {self.name_of_years(age_to)}')
            return
        except NameError:
            self.send_message(user_id, f'Вы ввели неправильное числовое значение. Повторите ввод.')
            return
        except ValueError:
            self.send_message(user_id, f'Вы ввели неправильное числовое значение. Повторите ввод.')
            return

    def get_years_of_person(self, bdate: str) -> object:
        bdate_splited = bdate.split(".")
        today = date.today()
        month = ""
        try:
            age = today.year - int(bdate_splited[2]) - ((today.month, today.day) < (int(bdate_splited[1]), int(bdate_splited[0])))
            return self.name_of_years(age)
        except IndexError:
            birth_date = {
                "1": "января",
                "2": "февраля",
                "3": "марта",
                "4": "апреля",
                "5": "мая",
                "6": "июня",
                "7": "июля",
                "8": "августа",
                "9": "сентября",
                "10": "октября",
                "11": "ноября",
                "12": "декабря",
            }
            month = birth_date.get(bdate_splited[1])
            return f"День рождения {int(bdate_splited[0])} {month}."


    def get_age_of_user(self, user_id):
        global age_from, age_to
        try:
            info = self.vk_user_got_api.users.get(
                user_id = user_id,
                fields = 'bdate',
            )[0]['bdate']
            num_age = self.get_years_of_person(info).split()[0]
            age_from = num_age
            age_to = num_age
            if num_age == "День":
                print(f'Ваш {self.get_years_of_person(info)}')
                self.send_message(user_id,
                              f'Так как в ваших настройках установлено "Показывать только месяц и день рождения"! \n'
                              f'Бот не может найти пользователей вашего возраста'
                              f'Поэтому, введите возраст для поиска, например от 20 года до 25 лет, в формате : 20-25 (или для конкретного возраста, например 25 лет: 25'
                              )
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return self.input_age(user_id, age)
            return print(f'Поиск пользователя вашего возраста {self.name_of_years(age_to)}')
        except KeyError:
            print(f'День рождения скрыт настройками приватности!')
            self.send_message(user_id,
                          f'Так как в ваших настройках установлено "Не показывать дату рождения" \n '
                          f'Бот не может найти пользователей вашего возраста \n'
                          f'Поэтому, введите возраст для поиска, например от 20 года до 25 лет, в формате : 20-25 (или для конкретного возраста, например 25 лет: 25'
                          )
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return self.input_age(user_id, age)

    def get_city(self, user_id):
        global city_id, city_title
        self.send_message(user_id,
                      f'Найдем пользователей в вашем городе или в другом? \n'
                      f'Введите "Да" или "y", если в вашем \n'
                      f'Или введите название города, для поиска в другом городе, например: Москва'
                      )
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "да" or answer == "y":
                    info = self.vk_user_got_api.users.get(
                        user_id = user_id,
                        fields = "city"
                    )
                    city_id = info[0]['city']["id"]
                    city_title = info[0]['city']["title"]
                    return f' в городе {city_title}.'
                else:
                    cities = self.vk_user_got_api.database.getCities(
                        country_id = 1,
                        q = answer.capitalize(),
                        need_all = 1,
                        count = 1000
                    )['items']
                    for i in cities:
                        if i["title"] == answer.capitalize():
                            city_id = i["id"]
                            city_title = answer.capitalize()
                            return f' в городе {city_title}'

    def user_gender(self, user_id):
        info = self.vk_user_got_api.users.get(
            user_id = user_id,
            fields = "sex"
        )
        if info[0]['sex'] == 1:
            print(f'Ваш пол женский, ищем мужчину.')
            return 2
        elif info[0]['sex'] == 2:
            print(f'Ваш пол мужской, ищем женщину.')
            return 1
        else:
            print("Ошибка!")

    def looking_for_persons(self, user_id):
        global list_found_persons
        list_found_persons = []
        res = self.vk_user_got_api.users.search(
            sort = 0,
            city = city_id,
            hometown = city_title,
            sex = self.user_gender(user_id),
            status = 1,
            age_from = age_from,
            age_to = age_to,
            has_photo = 1,
            count = 1000,
            fields = "can_write_private_message, "
                   "city, "
                   "domain, "
                   "home_town, "
        )
        number = 0
        for person in res["items"]:
            if not person["is_closed"]:
                if "city" in person and person["city"]["id"] == city_id and person["city"]["title"] == city_title:
                    number += 1
                    id_vk = person["id"]
                    list_found_persons.append(id_vk)
        print(f'Бот нашел {number} открытых профилей из {res["count"]} найденных')
        return

    def photo_person(self, user_id):
        global attachments
        res = self.vk_user_got_api.photos.get(
            owner_id = user_id,
            album_id = "profile",
            extended = 1,
            count=30
        )
        dict_photos = dict()
        for i in res['items']:
            photo_id = str(i["id"])
            i_likes = i["likes"]
            if i_likes["count"]:
                likes = i_likes["count"]
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse = True)
        attachments = []
        photo_ids = []
        for i in list_of_ids:
            photo_ids.append(i[1])
        try:
            attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
            return attachments
        except IndexError:
            try:
                attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
                return attachments
            except IndexError:
                return print(f'Нет фото')

    def get_found_person_id(self):
        global unique_person_id, found_persons
        seen_person = []
        for i in check():
            seen_person.append(int(i[0]))
        if not seen_person:
            try:
                unique_person_id = list_found_persons[0]
                return unique_person_id
            except NameError:
                found_persons = 0
                return found_persons
        else:
            try:
                for ifp in list_found_persons:
                    if ifp in seen_person:
                        pass
                    else:
                        unique_person_id = ifp
                        return unique_person_id
            except NameError:
                found_persons = 0
                return found_persons

    def found_person_info(self, show_person_id):
        res = self.vk_user_got_api.users.get(
            user_ids = show_person_id,
            fields = "about, "
                   "activities, "
                   "bdate, "
                   "status, "
                   "can_write_private_message, "
                   "city, "
                   "common_count, "
                   "contacts, "
                   "domain, "
                   "home_town, "
                   "interests, "
                   "movies, "
                   "music, "
                   "occupation"
        )
        first_name = res[0]["first_name"]
        last_name = res[0]["last_name"]
        age = self.get_years_of_person(res[0]["bdate"])
        vk_link = 'vk.com/' + res[0]["domain"]
        city = ''
        try:
            if res[0]["city"]["title"] is not None:
                city = f'Город {res[0]["city"]["title"]}'
            else:
                city = f'Город {res[0]["home_town"]}'
        except KeyError:
            pass
        print(f'{first_name} {last_name}, {age}, {city}. {vk_link}')
        return f'{first_name} {last_name}, {age}, {city}. {vk_link}'

    def send_photo(self, user_id, message, attachments):
        try:
            self.vk_group_got_api.messages.send(
                user_id = user_id,
                message = message,
                random_id = randrange(10 ** 7),
                attachment=",".join(attachments)
            )
        except TypeError:
            pass

    def show_found_person(self, user_id):
        print(self.get_found_person_id())
        if self.get_found_person_id() == None:
            self.send_message(user_id,
                          f'Все анкеты ранее были просмотрены. Будет выполнен новый поиск. /n'
                          f'Измените критерии поиска (возраст, город). /n'
                          f'Введите возраст поиска, на пример от 20 года и до 25 лет, /n'
                          f'в формате : 20-25 (или для конкретного возраста, например 25 лет: 25).')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    self.input_age(user_id, age)
                    self.get_city(user_id)
                    self.looking_for_persons(user_id)
                    self.show_found_person(user_id)
                    return
        else:
            self.send_message(user_id, self.found_person_info(self.get_found_person_id()))
            self.send_photo(user_id, 'Фото с максимальными лайками',
                            self.photo_person(self.get_found_person_id()))
            insert_data_seen_person(self.get_found_person_id())


bot = Bot()