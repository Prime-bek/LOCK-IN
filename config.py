import os
from dataclasses import dataclass

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN!")

# Admin ID (твой ID)
ADMIN_ID = 1265652628

# База данных
DB_PATH = os.getenv("DB_PATH", "bot.db")

# Категории задач
CATEGORIES = {
    "knowledge": {"emoji": "📚", "name_ru": "Знания", "name_uz": "Bilim"},
    "skill": {"emoji": "🎬", "name_ru": "Навыки", "name_uz": "Ko'nikma"},
    "body": {"emoji": "💪", "name_ru": "Тело", "name_uz": "Jismoniy"},
    "mind": {"emoji": "🧠", "name_ru": "Разум", "name_uz": "Aql"}
}

# Тексты
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в Life OS!\n\nПрокачивай себя как в RPG. Выбери язык:",
        "menu": "📋 Главное меню:",
        "add_task": "➕ Добавить задачу",
        "my_tasks": "📋 Мои задачи",
        "progress": "📊 Мой прогресс",
        "leaderboard": "🏆 Рейтинг",
        "journal": "🧠 Дневник",
        "settings": "⚙️ Настройки",
        "streak": "🔥 Streak",
        "achievements": "🏅 Достижения",
        "start_day": "🚀 Начать день",
        "delete_task": "🗑 Удалить задачу",
        "back": "◀️ Назад",
        "cancel": "❌ Отмена",
        "level_up": "🎉 LEVEL UP!\nТы достиг уровня {level}!",
        "xp_gained": "✅ +{xp} XP получено!",
        "enter_task_name": "Введи название задачи:",
        "select_category": "Выбери категорию:",
        "enter_xp": "Введи количество XP (1-100):",
        "task_created": "✅ Задача создана!",
        "no_tasks": "У тебя пока нет задач.",
        "select_task": "Выбери задачу для выполнения:",
        "journal_q1": "🌙 Что сегодня улучшило тебя?",
        "journal_q2": "📈 Что завтра сделать лучше?",
        "journal_saved": "✅ Запись сохранена! +5 XP",
        "streak_broken": "😢 Streak сброшен. Не сдавайся!",
        "streak_bonus": "🔥 Бонус за {days} дней подряд: +{xp} XP!",
        "admin_panel": "🔐 Админ-панель\n\nВсего пользователей: {total}\nАктивных (7 дней): {active}\nНеактивных: {inactive}",
        "admin_users_list": "📋 Список пользователей ({filter}):\n\n",
    },
    "uz": {
        "welcome": "👋 Life OS'ga xush kelibsiz!\n\nO'zingizni RPG'da rivojlantiring. Tilni tanlang:",
        "menu": "📋 Asosiy menyu:",
        "add_task": "➕ Vazifa qo'shish",
        "my_tasks": "📋 Mening vazifalarim",
        "progress": "📊 Mening rivojlanishim",
        "leaderboard": "🏆 Reyting",
        "journal": "🧠 Kundalik",
        "settings": "⚙️ Sozlamalar",
        "streak": "🔥 Ketma-ketlik",
        "achievements": "🏅 Yutuqlar",
        "start_day": "🚀 Kunni boshlash",
        "delete_task": "🗑 Vazifani o'chirish",
        "back": "◀️ Orqaga",
        "cancel": "❌ Bekor qilish",
        "level_up": "🎉 LEVEL UP!\nSiz {level} darajasiga yetdingiz!",
        "xp_gained": "✅ +{xp} XP olindi!",
        "enter_task_name": "Vazifa nomini kiriting:",
        "select_category": "Kategoriyani tanlang:",
        "enter_xp": "XP miqdorini kiriting (1-100):",
        "task_created": "✅ Vazifa yaratildi!",
        "no_tasks": "Sizda hali vazifalar yo'q.",
        "select_task": "Bajarish uchun vazifani tanlang:",
        "journal_q1": "🌙 Bugun sizni nima yaxshilab qo'ydi?",
        "journal_q2": "📈 Ertaga nima yaxshiroq qilish mumkin?",
        "journal_saved": "✅ Yozuv saqlandi! +5 XP",
        "streak_broken": "😢 Ketma-ketlik uzildi. Tushkunlikka tushmang!",
        "streak_bonus": "🔥 {days} kun ketma-ketlik bonusi: +{xp} XP!",
        "admin_panel": "🔐 Admin panel\n\nJami foydalanuvchilar: {total}\nFaol (7 kun): {active}\nFaol emas: {inactive}",
        "admin_users_list": "📋 Foydalanuvchilar ro'yxati ({filter}):\n\n",
    }
}

# Уровни
LEVELS = {1: "Beginner", 5: "Novice", 10: "Adept", 20: "Expert", 30: "Master", 50: "Legend"}