import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str

# Токен бота из переменных окружения Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка на случай если забыл установить переменную
if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN не найден!\n"
        "Установи переменную окружения BOT_TOKEN в Railway:\n"
        "Variables → New Variable → BOT_TOKEN = твой_токен"
    )

# Путь к базе данных (Railway предоставляет Volume или можно использовать PostgreSQL)
# Для SQLite на Railway Volume:
DB_PATH = os.getenv("DB_PATH", "/data/los_bot.db")

# Для PostgreSQL (если решишь перейти позже):
# DATABASE_URL = os.getenv("DATABASE_URL")

# Остальной код без изменений...

# Путь к базе данных
DB_PATH = "los_bot.db"

# Состояния для FSM
@dataclass
class States:
    # Добавление задачи
    TASK_NAME = "task_name"
    TASK_CATEGORY = "task_category"
    TASK_XP = "task_xp"
    
    # Дневник
    JOURNAL_Q1 = "journal_q1"
    JOURNAL_Q2 = "journal_q2"
    
    # Настройки
    SETTINGS_LANG = "settings_lang"

# Категории задач
CATEGORIES = {
    "knowledge": {"emoji": "🎓", "name_ru": "Знания", "name_uz": "Bilim"},
    "skill": {"emoji": "🎬", "name_ru": "Навыки", "name_uz": "Ko'nikma"},
    "body": {"emoji": "💪", "name_ru": "Тело", "name_uz": "Jismoniy"},
    "mind": {"emoji": "🧠", "name_ru": "Разум", "name_uz": "Aql"}
}

# Тексты на разных языках
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в Life OS!\n\nПрокачивай себя как в RPG.",
        "menu": "📋 Главное меню:",
        "add_task": "➕ Добавить задачу",
        "my_tasks": "📅 Мои задачи",
        "progress": "📊 Мой прогресс",
        "leaderboard": "🏆 Рейтинг",
        "journal": "🧠 Дневник",
        "settings": "⚙️ Настройки",
        "streak": "🔥 Streak",
        "achievements": "🏅 Достижения",
        "start_day": "🚀 Начать день",
        "add_completion": "⚡ Добавить выполнение",
        "delete_task": "🗑 Удалить задачу",
        "back": "◀️ Назад",
        "cancel": "❌ Отмена",
        "level_up": "🎉 LEVEL UP!\nВы достигли уровня {level}!",
        "xp_gained": "✅ +{xp} XP получено!",
        "enter_task_name": "Введите название задачи:",
        "select_category": "Выберите категорию:",
        "enter_xp": "Введите количество XP (число):",
        "task_created": "✅ Задача создана!",
        "no_tasks": "У вас пока нет задач.",
        "select_task": "Выберите задачу для выполнения:",
        "journal_q1": "🌙 Что сегодня улучшило тебя?",
        "journal_q2": "📈 Что завтра сделать лучше?",
        "journal_saved": "✅ Запись сохранена! +5 XP",
        "streak_broken": "😢 Streak сброшен. Не сдавайся!",
        "streak_bonus": "🔥 Бонус за {days} дней подряд: +{xp} XP!",
    },
    "uz": {
        "welcome": "👋 Life OS'ga xush kelibsiz!\n\nO'zingizni RPG'da rivojlantiring.",
        "menu": "📋 Asosiy menyu:",
        "add_task": "➕ Vazifa qo'shish",
        "my_tasks": "📅 Mening vazifalarim",
        "progress": "📊 Mening rivojlanishim",
        "leaderboard": "🏆 Reyting",
        "journal": "🧠 Kundalik",
        "settings": "⚙️ Sozlamalar",
        "streak": "🔥 Ketma-ketlik",
        "achievements": "🏅 Yutuqlar",
        "start_day": "🚀 Kunni boshlash",
        "add_completion": "⚡ Bajarish qo'shish",
        "delete_task": "🗑 Vazifani o'chirish",
        "back": "◀️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "level_up": "🎉 LEVEL UP!\nSiz {level} darajasiga yetdingiz!",
        "xp_gained": "✅ +{xp} XP olindi!",
        "enter_task_name": "Vazifa nomini kiriting:",
        "select_category": "Kategoriyani tanlang:",
        "enter_xp": "XP miqdorini kiriting (raqam):",
        "task_created": "✅ Vazifa yaratildi!",
        "no_tasks": "Sizda hali vazifalar yo'q.",
        "select_task": "Bajarish uchun vazifani tanlang:",
        "journal_q1": "🌙 Bugun sizni nima yaxshilab qo'ydi?",
        "journal_q2": "📈 Ertaga nima yaxshiroq qilish mumkin?",
        "journal_saved": "✅ Yozuv saqlandi! +5 XP",
        "streak_broken": "😢 Ketma-ketlik uzildi. Tushkunlikka tushmang!",
        "streak_bonus": "🔥 {days} kun ketma-ketlik bonusi: +{xp} XP!",
    }
}

# Уровни
LEVELS = {
    1: "Beginner",
    5: "Focused",
    10: "Builder",
    20: "Disciplined",
    30: "Elite",
    50: "Master"
}

# XP за действия
XP_REWARDS = {
    "study_hour": 15,
    "skill_hour": 20,
    "book_pages": 10,  # за 10 страниц
    "sport_20min": 15,
    "journal": 5,
    "streak_3": 20,
    "streak_7": 50,
    "level_up": 0  # специальная обработка
}