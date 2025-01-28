from sqlalchemy import Table, Column, Integer, ForeignKey
from database.base import Base

# Association table for many-to-many relationship between User and Circle (Group)
group_members = Table(
    'group_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('circle_id', Integer, ForeignKey('circle.id'), primary_key=True)
)
