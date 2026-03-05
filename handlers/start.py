from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import get_main_menu, get_language_keyboard
from utils import get_text

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()
    
    # Получаем или создаем пользователя
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username
    )
    
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("welcome", lang),
        reply_markup=get_main_menu(lang)
    )

@router.message(F.text.in_(["🚀 Начать день", "🚀 Kunni boshlash"]))
async def start_day(message: Message):
    """Начать день - проверка streak"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    # Обновляем streak
    streak_result = await db.update_streak(message.from_user.id)
    
    texts = []
    
    # Проверяем сообщения о streak
    if streak_result["message"] == "broken":
        texts.append(get_text("streak_broken", lang))
    elif streak_result["message"] == "streak_3":
        texts.append(get_text("streak_bonus", lang, days=3, xp=20))
        # Начисляем бонус
        await db.add_xp(message.from_user.id, 20)
    elif streak_result["message"] == "streak_7":
        texts.append(get_text("streak_bonus", lang, days=7, xp=50))
        await db.add_xp(message.from_user.id, 50)
    
    texts.append(f"🔥 Current streak: {streak_result['streak']} days")
    texts.append(get_text("menu", lang))
    
    await message.answer(
        "\n\n".join(texts),
        reply_markup=get_main_menu(lang)
    )

@router.message(F.text.in_(["◀️ Назад", "◀️ Orqaga"]))
async def back_to_menu(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )