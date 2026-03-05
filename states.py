from aiogram.fsm.state import State, StatesGroup

class AddTask(StatesGroup):
    """Состояния добавления задачи"""
    name = State()
    category = State()
    xp = State()

class JournalEntry(StatesGroup):
    """Состояния записи в дневник"""
    q1 = State()
    q2 = State()

class Settings(StatesGroup):
    """Настройки"""
    language = State()