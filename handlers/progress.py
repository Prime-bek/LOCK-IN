from aiogram import Router, F
from aiogram.types import Message

from database import db
from keyboards import get_main_menu
from utils import format_progress, get_text

router = Router()

@router.message(F.text.in_(["📊 Мой прогресс", "📊 Mening rivojlanishim"]))
async def show_progress(message: Message):
    """Показать прогресс пользователя"""
    stats = await db.get_user_stats(message.from_user.id)
    lang = stats["user"].get("language", "ru")
    
    text = format_progress(stats, lang)
    
    await message.answer(text, reply_markup=get_main_menu(lang))

@router.message(F.text.in_(["🔥 Streak", "🔥 Ketma-ketlik"]))
async def show_streak(message: Message):
    """Показать streak"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        f"🔥 Your current streak: {user['streak']} days\n\n"
        f"Keep going to earn bonuses!\n"
        f"3 days = +20 XP\n"
        f"7 days = +50 XP\n"
        f"30 days = Achievement",
        reply_markup=get_main_menu(lang)
    )

@router.message(F.text.in_(["🏅 Достижения", "🏅 Yutuqlar"]))
async def show_achievements(message: Message):
    """Показать достижения (заглушка)"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    # Здесь можно добавить логику достижений
    await message.answer(
        "🏅 Достижения скоро будут доступны!\n\n"
        "Список достижений:\n"
        "🔥 7 Day Streak\n"
        "📚 First Book\n"
        "💪 10 Workouts\n"
        "🎬 First Skill Task\n"
        "⚡ Level 10\n"
        "🏆 Top 10 Leaderboard",
        reply_markup=get_main_menu(lang)
    )