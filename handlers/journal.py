from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import get_main_menu, get_cancel_keyboard
from states import JournalEntry
from utils import get_text

router = Router()

@router.message(F.text.in_(["🧠 Дневник", "🧠 Kundalik"]))
async def start_journal(message: Message, state: FSMContext):
    """Начать запись в дневник"""
    await state.set_state(JournalEntry.q1)
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("journal_q1", lang),
        reply_markup=get_cancel_keyboard(lang)
    )

@router.message(JournalEntry.q1)
async def process_journal_q1(message: Message, state: FSMContext):
    """Первый вопрос дневника"""
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await cancel_journal(message, state)
        return
    
    await state.update_data(q1=message.text)
    await state.set_state(JournalEntry.q2)
    
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(get_text("journal_q2", lang))

@router.message(JournalEntry.q2)
async def process_journal_q2(message: Message, state: FSMContext):
    """Второй вопрос и сохранение"""
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await cancel_journal(message, state)
        return
    
    data = await state.get_data()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    # Сохраняем в базу
    await db.save_journal_entry(
        message.from_user.id,
        data["q1"],
        message.text
    )
    
    # Начисляем XP за дневник
    await db.add_xp(message.from_user.id, 5, "mind")
    
    await state.clear()
    
    await message.answer(
        get_text("journal_saved", lang),
        reply_markup=get_main_menu(lang)
    )

async def cancel_journal(message: Message, state: FSMContext):
    """Отмена записи в дневник"""
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )