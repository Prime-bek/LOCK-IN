from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards import (
    get_main_menu, get_categories_keyboard, get_tasks_keyboard,
    get_delete_tasks_keyboard, get_cancel_keyboard
)
from states import AddTask
from utils import get_text

router = Router()

# ========== ДОБАВЛЕНИЕ ЗАДАЧИ ==========

@router.message(F.text.in_(["➕ Добавить задачу", "➕ Vazifa qo'shish"]))
async def add_task_start(message: Message, state: FSMContext):
    """Начало добавления задачи"""
    await state.set_state(AddTask.name)
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("enter_task_name", lang),
        reply_markup=get_cancel_keyboard(lang)
    )

@router.message(AddTask.name)
async def process_task_name(message: Message, state: FSMContext):
    """Обработка названия задачи"""
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await cancel_add_task(message, state)
        return
    
    await state.update_data(name=message.text)
    await state.set_state(AddTask.category)
    
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("select_category", lang),
        reply_markup=get_categories_keyboard(lang)
    )

@router.callback_query(AddTask.category, F.data.startswith("cat_"))
async def process_task_category(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category = callback.data.replace("cat_", "")
    await state.update_data(category=category)
    await state.set_state(AddTask.xp)
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user.get("language", "ru")
    
    await callback.message.edit_text(get_text("enter_xp", lang))

@router.message(AddTask.xp)
async def process_task_xp(message: Message, state: FSMContext):
    """Обработка XP и создание задачи"""
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await cancel_add_task(message, state)
        return
    
    try:
        xp = int(message.text)
        if xp <= 0 or xp > 1000:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите число от 1 до 1000:")
        return
    
    data = await state.get_data()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    # Создаем задачу
    task_id = await db.create_task(
        message.from_user.id,
        data["name"],
        data["category"],
        xp
    )
    
    await state.clear()
    
    await message.answer(
        get_text("task_created", lang),
        reply_markup=get_main_menu(lang)
    )

async def cancel_add_task(message: Message, state: FSMContext):
    """Отмена добавления задачи"""
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )

# ========== МОИ ЗАДАЧИ ==========

@router.message(F.text.in_(["📅 Мои задачи", "📅 Mening vazifalarim"]))
async def show_tasks(message: Message):
    """Показать список задач"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    tasks = await db.get_user_tasks(message.from_user.id)
    
    if not tasks:
        await message.answer(get_text("no_tasks", lang))
        return
    
    await message.answer(
        get_text("select_task", lang),
        reply_markup=get_tasks_keyboard(tasks, lang)
    )

@router.callback_query(F.data.startswith("complete_"))
async def complete_task(callback: CallbackQuery):
    """Выполнение задачи"""
    task_id = int(callback.data.replace("complete_", ""))
    
    result = await db.complete_task(callback.from_user.id, task_id)
    
    if not result:
        await callback.answer("Задача не найдена!")
        return
    
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user.get("language", "ru")
    
    # Формируем сообщение
    texts = [
        f"✅ {result['task_name']}",
        get_text("xp_gained", lang, xp=result['xp'])
    ]
    
    if result["leveled_up"]:
        texts.append(get_text("level_up", lang, level=result["new_level"]))
    
    await callback.message.edit_text("\n\n".join(texts))
    await callback.answer()

# ========== УДАЛЕНИЕ ЗАДАЧИ ==========

@router.message(F.text.in_(["🗑 Удалить задачу", "🗑 Vazifani o'chirish"]))
async def delete_task_start(message: Message):
    """Начало удаления задачи"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    tasks = await db.get_user_tasks(message.from_user.id)
    
    if not tasks:
        await message.answer(get_text("no_tasks", lang))
        return
    
    await message.answer(
        "Выберите задачу для удаления:",
        reply_markup=get_delete_tasks_keyboard(tasks)
    )

@router.callback_query(F.data.startswith("delete_"))
async def confirm_delete(callback: CallbackQuery):
    """Удаление задачи"""
    task_id = int(callback.data.replace("delete_", ""))
    
    await db.delete_task(task_id, callback.from_user.id)
    
    await callback.message.edit_text("✅ Задача удалена!")
    await callback.answer()