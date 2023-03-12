import random
from random import randrange
import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy_utils import database_exists, create_database
from database import create_tables, drop_tables, User, User_search_data, White_list, Black_list
from sqlalchemy.exc import IntegrityError, InvalidRequestError, PendingRollbackError

url_object = URL.create(
    'postgresql',
    username='postgres',
    password='BorgH8417',
    host='localhost',
    database='VKinderDB',
)


"""Creating engine"""
engine = create_engine(url_object)


"""Creating database."""
if not database_exists(engine.url):
    create_database(engine.url)

"""Droping existing tables"""
drop_tables(engine)
"""Creating tables"""
create_tables(engine)

Session = sessionmaker(bind=engine)
metadata = MetaData(bind=engine)

session = Session()


"""Links to vk_tokens."""
with open('bot_token.txt', 'r') as file:
    bot_token = file.readline()
with open('user_token.txt', 'r') as file:
    user_token = file.readline()

vk = vk_api.VkApi(token=bot_token)
vk2 = vk_api.VkApi(token=user_token)
longpoll = VkLongPoll(vk)


"""Function for sending messages to user."""


def write_msg(user_id, message, attachment):
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'attachment': attachment,  'random_id': randrange(10 ** 7)})


"""Getting user data."""


def get_user_data(user_id):
    user_data = {}
    resp = vk.method('users.get', {'user_id': user_id,
                                   'v': 5.131,
                                   'fields': 'first name, last name, bdate, sex, city'})
    if resp:
        for key, value in resp[0].items():
            if key == 'city':
                user_data[key] = value['id']
            else:
                user_data[key] = value
    else:
        write_msg(user_id, 'Ошибка', None)
        return False
    return user_data


"""Gathering info for missing user details and creating keys for missing data."""


def check_missing_info(user_data):
    for item in ['bdate', 'city']:
        if not user_data.get(item):
            user_data[item] = ''
    if user_data.get('bdate'):
        if len(user_data['bdate'].split('.')) != 3:
            user_data[item] = ''
    return user_data


"""Checking user birthday date and filling it with user input date."""


def check_bdate(user_data, user_id):
    for item_dict in [user_data]:
        if len(item_dict['bdate'].split('.')) != 3:
            write_msg(user_id, f'Введите дату рождения в формате "ХХ.ХХ.ХХХХ:"', None)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_data['bdate'] = event.text
                    return user_data
        else:
            return user_data


"""Function to transform city name into city id."""


def city_id(city_name):
    resp = vk2.method('database.getCities', {
                    'country_id': 1,
                    'q': f'{city_name}',
                    'need_all': 0,
                    'count': 1000,
                    'v': 5.131})
    if resp:
        if resp.get('items'):
            return resp.get('items')
        write_msg(city_name, 'Ошибка ввода города', None)
        return False


"""Checking user city and filling it with user input city."""


def check_city(user_data, user_id):
    for item_dict in [user_data]:
        if item_dict['city'] == '':
            write_msg(user_id, f'Введите город:', None)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_data['city'] = city_id(event.text)[0]['id']
                    return user_data
        else:
            return user_data


"""Counting users age."""


def get_age(user_data):
    for key, value in user_data:
        user_data['age'] = datetime.datetime.now().year - int(user_data['bdate'][-4:])
        return user_data


"""Searching for pair, accordind to parameters."""


def user_search(user_data):
    resp = vk2.method('users.search', {
                                'age_from': user_data['age'] - 3,
                                'age_to': user_data['age'] + 3,
                                'city': user_data['city'],
                                'sex': 3 - user_data['sex'],
                                'relation': 6,
                                'status': 1,
                                'has_photo': 1,
                                'count': 1000,
                                'v': 5.131})
    if resp:
        if resp.get('items'):
            return resp.get('items')
        write_msg(user_data['id'], 'Ошибка', None)
        return False


"""Filtering open accounts."""


def get_users_list(users_data):
    not_private_list = []
    for person_dict in users_data:
        if person_dict.get('is_closed') == False:
            not_private_list.append(
                            {'first_name': person_dict.get('first_name'), 'last_name': person_dict.get('last_name'),
                             'id': person_dict.get('id'), 'vk_link':   'vk.com/id'+str(person_dict.get('id')),
                             'is_closed': person_dict.get('is_closed')
                             })
        else:
            continue
    return not_private_list


"""Combining user data."""


def combine_user_data(user_id):
    user_data = [get_age(check_city(check_bdate(check_missing_info(get_user_data(user_id)), user_id), user_id))]
    return user_data


"""Combining users search data."""


def combine_users_data(user_id):
    users_data = get_users_list(
        user_search(get_age(check_city(check_bdate(check_missing_info(get_user_data(user_id)), user_id), user_id))))
    return users_data


"""Getting random account from dictionary."""


def get_random_user(users_data):
    return random.choice(users_data)


"""Getting photos from vk."""


def get_photos(vk_id):

    resp = vk2.method('photos.getAll', {
            'owner_id': vk_id,
            'album_id': 'profile',
            'extended': 'likes',
            'count': 25
        })
    if resp:
        if resp.get('items'):
            return resp.get('items')
        write_msg(vk_id, 'Ошибка', None)
        return False


"""Sorting photos by number of likes."""


def sort_by_likes(photos_dict):
    photos_by_likes_list = []

    for photos in photos_dict:
        likes = photos.get('likes')
        photos_by_likes_list.append([photos.get('owner_id'), photos.get('id'), likes.get('count')])
    photos_by_likes_list = sorted(photos_by_likes_list, key=lambda x: x[2], reverse=True)
    return photos_by_likes_list


"""Getting 3 first photos with max likes."""


def get_photos_list(sort_list):
    photos_list = []
    count = 0
    for photos in sort_list:
        photos_list.append('photo'+str(photos[0])+'_'+str(photos[1]))
        count += 1
        if count == 3:
            return photos_list


"""Filling user table."""


def fill_user_table(user_data):
    for item in user_data:
        user_record = session.query(User).filter_by(id=item['id']).scalar()
        if not user_record:
            user_record = User(id=item['id'], bdate=item['bdate'], city=item['city'], sex=item['sex'],
                               first_name=item['first_name'], last_name=item['last_name'],
                               can_access_closed=item['can_access_closed'], is_closed=item['is_closed'],
                               age=item['age']
                               )
        session.add(user_record)
    return session.commit()


"""Filling search table."""


def fill_user_search_table(users_data):
    try:
        for item in users_data:
            users_record = session.query(User_search_data).filter_by(id=item['id']).scalar()
            if not users_record:
                users_record = User_search_data(
                                   id=item['id'], first_name=item['first_name'], last_name=item['last_name'],
                                   vk_link=item['vk_link'], is_closed=item['is_closed']
                                                )
            session.add(users_record)
            session.commit()
        return True
    except (IntegrityError, InvalidRequestError, PendingRollbackError):
        session.rollback()
        return False


"""Filling white_list table."""


def fill_white_list(random_choice):
    for item in random_choice:
        random_user_record = session.query(White_list).filter_by(id=item['id']).scalar()
        if not random_user_record:
            random_user_record = White_list(id=item['id'], first_name=item['first_name'], last_name=item['last_name'],
                                            vk_link=item['vk_link'], is_closed=item['is_closed']
                                            )
        session.add(random_user_record)
    return session.commit()


"""Filling black_list table."""


def fill_black_list(random_choice):
    for item in random_choice:
        random_user_record = session.query(Black_list).filter_by(id=item['id']).scalar()
        if not random_user_record:
            random_user_record = Black_list(id=item['id'], first_name=item['first_name'], last_name=item['last_name'],
                               vk_link=item['vk_link'], is_closed=item['is_closed']
                                            )
        session.add(random_user_record)
    return session.commit()


"""Getting list of favorites."""


def check_db_favorites():
    db_favorites = session.query(White_list).order_by(White_list.user_id).all()
    all_users = []
    for item in db_favorites:
        all_users.append([item.user_id, 'id:'+item.id, item.first_name+' '+item.last_name, item.vk_link+' '])
    return all_users


"""Function for new bot messages"""


def loop_bot():
    for this_event in longpoll.listen():
        if this_event.type == VkEventType.MESSAGE_NEW:
            if this_event.to_me:
                message_text = this_event.text
                return message_text
