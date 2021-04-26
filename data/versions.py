import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Versions(SqlAlchemyBase):
    __tablename__ = 'versions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    photo = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    version_id = sqlalchemy.Column(sqlalchemy.Integer)  # sqlalchemy.ForeignKey("users.id"))
    # user = orm.relation('User')
    # products = orm.relation("Products", back_populates='user')