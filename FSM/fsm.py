from aiogram.fsm.state import State, StatesGroup


class FSMUsername(StatesGroup):
    username_write = State()


class FSMHelp(StatesGroup):
    view_help = State()


class AddTransition(StatesGroup):
    transaction_select_name = State()

    choose_action = State()
    select_category = State()
    writing_digit = State()
    writing_comment = State()

    transaction_select_category = State()   # Пользователь выбирает категорию
    transaction_expenses_digit = State()    # Пользователь вводит сумму Расходов
    transaction_expenses_comment = State()  # Пользователь вводит комментарий для расходов
    income_select_category = State()
    income_digit = State()                  # Пользователь вводит число для распределения средств
    transaction_salary_digit = State()      # Пользователь вводит сумму Доходов
    transaction_salary_comment = State()    # Пользователь вводит комментарий для Доходов


# Класс для управления состояниями, связанными со статистикой
class FSMStats(StatesGroup):
    stat_choice = State()  # Состояние для выбора типа статистики
    stat_day = State()     # Состояние для выбора дня статистики
    view_day = State()     # Состояние для просмотра статистики за день


class FSMViewUsers(StatesGroup):
    view_user = State()
