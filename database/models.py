import datetime
from typing import Annotated
from sqlalchemy import Table, Column, BIGINT, String, MetaData, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base
import enum


intpk_BI = Annotated[int, mapped_column(BIGINT, primary_key=True)]
intpk_BI_N = Annotated[int, mapped_column(BIGINT, primary_key=False)]
intpk_def = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created = Annotated[datetime.datetime, mapped_column(default=datetime.datetime.now)]


class UsersBot(Base):
    __tablename__ = 'bot_users'

    user_id: Mapped[intpk_BI]
    username: Mapped[str]
    balance: Mapped[float]
    is_admin: Mapped[bool]


class UserSalary(Base):
    __tablename__ = 'user_salary'

    salary_id: Mapped[intpk_def]
    user_id: Mapped[intpk_BI]
    amount: Mapped[float]
    date_of_receip: Mapped[created]
    description: Mapped[str]


class UserExpenses(Base):
    __tablename__ = 'user_expenses'

    expense_id: Mapped[intpk_def]
    user_id: Mapped[intpk_BI]
    amount: Mapped[float]
    date_of_expenditure: Mapped[created]
    description: Mapped[str]


class UserCategories(Base):
    __tablename__ = 'user_categories'

    user_categories_id = Mapped[intpk_def]
    user_id: Mapped[intpk_BI]
    categories: Mapped[str]
    amount: Mapped[float]
