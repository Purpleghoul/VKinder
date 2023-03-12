import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()

"""Creating classes"""


class User(Base):
    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, unique=True)
    bdate = sq.Column(sq.Date)
    city = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    can_access_closed = sq.Column(sq.Boolean, nullable=False)
    is_closed = sq.Column(sq.Boolean, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)

    def __str__(self):
        return f'User {self.id}: {self.user_id}, {self.bdate}, {self.city}, {self.sex}, {self.first_name},' \
               f'{self.last_name}, {self.can_access_closed},{self.is_closed}, {self.age}'


class User_search_data(Base):

    __tablename__ = 'user_search_data'

    user_id = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    vk_link = sq.Column(sq.String, unique=True, nullable=False)
    is_closed = sq.Column(sq.Boolean, nullable=False)

    def __str__(self):
        return f'User_search_data {self.id}: {self.user_id}, {self.first_name},' \
               f'{self.last_name}, {self.vk_link},{self.is_closed}'


class White_list(Base):

    __tablename__ = 'white_list'

    user_id = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    vk_link = sq.Column(sq.String, unique=True, nullable=False)
    is_closed = sq.Column(sq.Boolean, nullable=False)

    def __str__(self):
        return f'White_list {self.id}: {self.user_id}, {self.first_name},' \
               f'{self.last_name}, {self.vk_link},{self.is_closed}'


class Black_list(Base):
    __tablename__ = 'black_list'

    user_id = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    last_name = sq.Column(sq.String, nullable=False)
    vk_link = sq.Column(sq.String, unique=True, nullable=False)
    is_closed = sq.Column(sq.Boolean, nullable=False)

    def __str__(self):
        return f'Black_list {self.id}: {self.user_id}, {self.first_name},' \
               f'{self.last_name}, {self.vk_link},{self.is_closed}'


"""Function to create all tables."""


def create_tables(engine):
    Base.metadata.create_all(engine)


"""Function to drop all tables."""


def drop_tables(engine):
    Base.metadata.drop_all(engine)