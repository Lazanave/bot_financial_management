import datetime
import logging
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import UsersBot, UserSalary, UserExpenses, UserCategories


class AsyncORM:
    def __init__(self, session: AsyncSession):
        self.session = session  # Инициализируем сессию для работы с базой данных

    async def _execute_query(self, query):
        async with self.session.begin():  # Начинаем асинхронную транзакцию
            res = await self.session.execute(query)  # Асинхронно выполняем запрос
            return res

    # Проверяем, есть ли пользователь в базе
    async def user_in_db(self, uid: int) -> bool:
        query = select(UsersBot.user_id).filter_by(user_id=uid)  # Формируем SQL-запрос для выбора user_id
        result = await self._execute_query(query)  # Выполняем запрос
        user_exists = result.one_or_none() is not None  # Проверяем, найден ли пользователь
        return user_exists

    # Возвращаем значение столбца is_admin
    async def is_admin(self, uid: int) -> bool:
        query = select(UsersBot.is_admin).filter_by(user_id=uid)  # Формируем SQL-запрос для выбора is_admin
        result = await self._execute_query(query)  # Выполняем запрос
        return result.scalar()  # Возвращаем результат проверки на администратора

    # Добавляем юзера
    async def insert_user(self, uid: int, user_name: str):
        user = UsersBot(user_id=uid, username=user_name, balance=0, is_admin=False)  # Создаем нового пользователя
        self.session.add(user)
        await self.session.commit()  # Асинхронно коммитим изменения в базе данных

    # Добавляем категории
    async def add_category(self, uid: int, categories: list):
        for category in categories:
            user_category = UserCategories(user_id=uid, categories=category, amount=0)
            self.session.add(user_category)
        await self.session.commit()

    # Выводим пользователю его юзернейм и баланс
    async def check_balance_username(self, uid: int):
        query = select(
            UsersBot.balance,
            UsersBot.username
        ).filter_by(user_id=uid)  # Формируем SQL-запрос для выбора баланса
        result = await self._execute_query(query)  # Выполняем запрос
        return result.fetchone()  # Возвращаем баланс пользователя

    async def category_balances(self, uid: int):
        query = select(
            UserCategories.categories,
            UserCategories.amount
        ).filter_by(user_id=uid)
        result = await self._execute_query(query)
        return result.fetchall()

    # Возвращаем категории
    async def user_categories(self, uid: int):
        query = select(UserCategories.categories).filter_by(user_id=uid)
        result = await self._execute_query(query)
        return result.scalars().all()

    # Обновления баланса после добавления дохода
    async def update_balance_salary(self, uid: int, amount: float, description: str):
        user = await self.session.get(UsersBot, uid)  # Получаем пользователя по id
        user.balance += amount  # Обновляем баланс пользователя

        info = UserSalary(user_id=uid, amount=amount, description=description)  # Создаем запись о доходе
        self.session.add(info)  # Добавляем запись в сессию

        await self.session.commit()  # Асинхронно коммитим изменения в базе данных
    #
    # # Обновления баланса после добавления расходов
    # async def update_balance_expenses(self, uid: int, amount: float, description: str, category: str):
    #     # 1 Нужно обновить баланс категории
    #     query = (
    #         update(UserCategories)
    #         .where(and_(UserCategories.user_id == uid, UserCategories.categories == category))
    #         .values(amount=UserCategories.amount - amount)
    #     )
    #     await self._execute_query(query)
    #     # 2 Нужно добавить операцию в базу
    #     info = UserExpenses(user_id=uid, amount=amount, description=description)  # Создаем запись о доходе
    #     self.session.add(info)  # Добавляем запись в сессию
    #     await self.session.commit()  # Асинхронно коммитим изменения в базе данных

    async def check_amount_category(self, uid: int, category: str):
        query = select(UserCategories.amount).filter_by(
            user_id=uid,
            categories=category
        )
        result = await self._execute_query(query)
        return result.scalar()

    # Обновление баланса в категории
    async def update_category_balance(self, uid: int, amount: float, category: str):
        query = (
            update(UserCategories)
            .where(and_(UserCategories.user_id == uid, UserCategories.categories == category))
            .values(amount=UserCategories.amount + amount)
        )
        await self._execute_query(query)
        user = await self.session.get(UsersBot, uid)
        user.balance -= amount
        await self.session.commit()
    #
    # # async def update_balance_expenses(self, uid: int, amount: float, description: str):
    # #     user = await self.session.get(UsersBot, uid)  # Получаем пользователя по id
    # #     user.balance -= amount  # Обновляем баланс пользователя
    # #
    # #     info = UserExpenses(user_id=uid, amount=amount, description=description)  # Создаем запись о доходе
    # #     self.session.add(info)  # Добавляем запись в сессию
    # #
    # #     await self.session.commit()  # Асинхронно коммитим изменения в базе данных
    #
    # async def return_salary_dates(self, uid: int):
    #     query = select(UserSalary.date_of_receip).filter_by(user_id=uid)  # Формируем SQL-запрос для выбора дат доходов
    #     result = await self._execute_query(query)  # Выполняем запрос
    #     return result.scalars().unique().all()  # Возвращаем уникальные даты доходов
    #
    # async def return_expenses_dates(self, uid: int):
    #     query = select(UserExpenses.date_of_expenditure).filter_by(user_id=uid)  # Формируем SQL-запрос для выбора дат доходов
    #     result = await self._execute_query(query)  # Выполняем запрос
    #     return result.scalars().unique().all()  # Возвращаем уникальные даты доходов
    #
    # async def return_info_statistics_day(self, uid: int, date: datetime.date, transaction: str) -> list:
    #     if transaction == 'salary':
    #         query = (
    #             select(UserSalary.amount, UserSalary.description, UserSalary.salary_id)
    #             .filter(and_(UserSalary.user_id == uid, UserSalary.date_of_receip == date))
    #         )
    #     elif transaction == 'expenses':
    #         query = (
    #             select(UserExpenses.amount, UserExpenses.description, UserExpenses.expense_id)
    #             .filter(and_(UserExpenses.user_id == uid, UserExpenses.date_of_expenditure == date))
    #         )
    #     result = await self._execute_query(query)  # Выполняем запрос
    #     return result.scalars().all()  # Возвращаем список результатов
    #
    # async def check_all_users(self) -> list:
    #     query = select(UsersBot.user_id)
    #     result = await self._execute_query(query)
    #     return result.scalars().all()
