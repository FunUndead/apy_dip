import requests
from settings import tokenapp
from database.queries import Queries
from database.inserts import Inserts
from database.base import DBSession


class VkRequest:

    url = 'https://api.vk.com/method/'

    MALE = 1
    FEMALE = 2
    HAS_PHOTO = 1  # 1 — искать только пользователей с фотографией, 0 — искать по всем пользователям.
    AGE_RANGE = 3  # Разница в возрасте для подбора пары.
    SORT = 0  # 1 — по дате регистрации, 0 — по популярности.

    def __init__(self):
        self.token = tokenapp
        self.version = 5.126
        self.params = {
            'access_token': self.token,
            'v': self.version
        }

    def search_cities(self, city):

        country_id = 1  # ID страны
        need_all = 0  # 1 – возвращать все города. 0 – возвращать только основные города.
        count = 1  # количество городов, которые необходимо вернуть.

        cities_url = self.url + 'database.getCities'
        cities_params = {
            'country_id': country_id,
            'q': city,
            'need_all': need_all,
            'count': count
        }
        res = requests.get(cities_url, params={**self.params, **cities_params})
        data = res.json()
        if data['response']['items']:
            return data['response']['items'][0]
        else:
            return None

    def get_userinfo(self, userid):
        get_userinfo_url = self.url + 'users.get'
        get_userinfo_params = {
            'user_id': userid,
            'fields': 'city,sex,bdate,relation'
        }
        get = requests.get(get_userinfo_url, params={**self.params, **get_userinfo_params})
        data = get.json()
        return data

    def search_matches(self, user_id):

        search_url = self.url + 'users.search'
        user = Queries(DBSession).get_user_db(user_id)
        age = int(user['age'])
        city = int(user['city'])
        sex = self.FEMALE

        if int(user['sex']) == self.MALE:
            sex = self.FEMALE
        if int(user['sex']) == self.FEMALE:
            sex = self.MALE
        search_params = {
            'sort': self.SORT,
            'city': city,
            'sex': sex,
            'age_from': age - self.AGE_RANGE,
            'age_to': age + self.AGE_RANGE,
            'has_photo': self.HAS_PHOTO,
            'fields': 'is_closed'
        }
        get = requests.get(search_url, params={**self.params, **search_params})
        data = get.json()
        Inserts(DBSession).insert_matches(data, user_id)
        return data

    def get_photos(self, match_id=None, number_of_photos=3):

        rev = 1  # порядок сортировки фотографий. Возможные значения: 1 — антихронологический, 0 — хронологический.
        count = 3  # Кол-во фотографий
        extended = 1  # 1 — будут возвращены дополнительные поля likes, comments, tags, can_comment, reposts.

        if match_id is None:
            match_id = 1
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': match_id,
            'album_id': 'profile',
            'extended': extended,
            'count': count,
            'rev': rev
        }
        res = requests.get(photos_url, params={**self.params, **photos_params})
        photos = []
        if len(res.json()['response']['items']) >= number_of_photos:
            for i in range(0, number_of_photos):
                photos.append([res.json()['response']['items'][i]['id'],
                               res.json()['response']['items'][i]['likes']['count']])
                photos.sort(key=lambda x: x[1], reverse=True)
                print(photos)
        else:
            photos.append([res.json()['response']['items'][0]['id'],
                          res.json()['response']['items'][0]['likes']['count']])
        return photos
