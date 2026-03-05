from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import db
from keyboards import get_main_menu, get_language_keyboard
from utils import get_text

router = Router()

@router.message(F.text.in_(["⚙️ Настройки", "⚙️ Sozlamalar"]))
async def show_settings(message: Message):
    """Показать настройки"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        f"⚙️ Settings\n\n"
        f"Current language: {lang.upper()}\n\n"
        f"Select language:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def change_language(callback: CallbackQuery):
    """Изменить язык"""
    new_lang = callback.data.replace("lang_", "")
    
    # Обновляем в базе
    async with db._connect() as conn:  # Нужно добавить метод или сделать через db
        pass  # Заглушка - нужно реализовать обновление языка
    
    await callback.message.edit_text(
        get_text("menu", new_lang),
        reply_markup=get_main_menu(new_lang)
    )
    await callback.answer()