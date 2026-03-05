from aiogram import Router, F
from aiogram.types import Message

from database import db
from keyboards import get_main_menu
from utils import format_leaderboard, get_text

router = Router()

@router.message(F.text.in_(["🏆 Leaderboard", "🏆 Reyting"]))
async def show_leaderboard(message: Message):
    """Показать таблицу лидеров"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    users = await db.get_leaderboard(10)
    text = format_leaderboard(users, lang)
    
    # Добавляем позицию пользователя
    stats = await db.get_user_stats(message.from_user.id)
    text += f"\n\n📍 Your position: #{stats['rank']}"
    
    await message.answer(text, reply_markup=get_main_menu(lang))