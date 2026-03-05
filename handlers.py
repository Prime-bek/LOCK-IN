from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TEXTS, CATEGORIES, LEVELS, ADMIN_ID
from database import db
from keyboards import (
    get_main_menu, get_categories_keyboard, get_tasks_keyboard,
    get_delete_tasks_keyboard, get_cancel_keyboard, get_language_keyboard,
    get_admin_keyboard, get_back_button
)

router = Router()

# ========== СОСТОЯНИЯ ==========
class AddTask(StatesGroup):
    name = State()
    category = State()
    xp = State()

class JournalEntry(StatesGroup):
    q1 = State()
    q2 = State()

# ========== ХЕЛПЕРЫ ==========
def get_level_title(level: int) -> str:
    """Получить название уровня"""
    max_title = "Beginner"
    for lvl, title in sorted(LEVELS.items()):
        if level >= lvl:
            max_title = title
    return max_title

def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить текст на нужном языке"""
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

# ========== СТАРТ И ЯЗЫК ==========
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()
    
    # Получаем или создаем пользователя
    user = await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username
    )
    
    # Если язык не выбран (первый вход) - показываем выбор языка
    if not user.get("language"):
        await message.answer(
            "👋 Добро пожаловать! / Welcome!\n\nВыбери язык / Tilni tanlang:",
            reply_markup=get_language_keyboard()
        )
        return
    
    lang = user.get("language", "ru")
    await message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )

@router.callback_query(F.data.startswith("lang_"))
async def change_language(callback: CallbackQuery):
    """Изменить язык"""
    new_lang = callback.data.replace("lang_", "")
    
    # Обновляем в базе
    await db.update_user_language(callback.from_user.id, new_lang)
    
    await callback.message.edit_text(
        get_text("menu", new_lang),
        reply_markup=get_main_menu(new_lang)
    )
    await callback.answer()

# ========== ГЛАВНОЕ МЕНЮ ==========
@router.message(F.text.in_([get_text("back", "ru"), get_text("back", "uz")]))
async def back_to_menu(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )

# ========== НАЧАТЬ ДЕНЬ ==========
@router.message(F.text.in_([get_text("start_day", "ru"), get_text("start_day", "uz")]))
async def start_day(message: Message):
    """Начать день - проверка streak"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    # Обновляем streak
    streak_result = await db.update_streak(message.from_user.id)
    
    texts = []
    
    # Проверяем сообщения о streak
    if streak_result["message"] == "broken":
        texts.append(get_text("streak_broken", lang, old_streak=streak_result.get("old_streak", 0)))
    elif streak_result["message"] == "streak_3":
        texts.append(get_text("streak_bonus", lang, days=3, xp=20))
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

# ========== ДОБАВЛЕНИЕ ЗАДАЧИ ==========
@router.message(F.text.in_([get_text("add_task", "ru"), get_text("add_task", "uz")]))
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
        await cancel_action(message, state)
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
    await callback.answer()

@router.message(AddTask.xp)
async def process_task_xp(message: Message, state: FSMContext):
    """Обработка XP и создание задачи"""
    if message.text in [get_text("cancel", "ru"), get_text("cancel", "uz")]:
        await cancel_action(message, state)
        return
    
    try:
        xp = int(message.text)
        if xp <= 0 or xp > 100:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите число от 1 до 100:")
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

async def cancel_action(message: Message, state: FSMContext):
    """Отмена действия"""
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )

# ========== МОИ ЗАДАЧИ ==========
@router.message(F.text.in_([get_text("my_tasks", "ru"), get_text("my_tasks", "uz")]))
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
@router.message(F.text.in_([get_text("delete_task", "ru"), get_text("delete_task", "uz")]))
async def delete_task_start(message: Message):
    """Начало удаления задачи"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    tasks = await db.get_user_tasks(message.from_user.id)
    
    if not tasks:
        await message.answer(get_text("no_tasks", lang))
        return
    
    await message.answer(
        "Выбери задачу для удаления:",
        reply_markup=get_delete_tasks_keyboard(tasks, lang)
    )

@router.callback_query(F.data.startswith("delete_"))
async def confirm_delete(callback: CallbackQuery):
    """Удаление задачи"""
    task_id = int(callback.data.replace("delete_", ""))
    
    await db.delete_task(task_id, callback.from_user.id)
    
    await callback.message.edit_text("✅ Задача удалена!")
    await callback.answer()

# ========== ПРОГРЕСС ==========
@router.message(F.text.in_([get_text("progress", "ru"), get_text("progress", "uz")]))
async def show_progress(message: Message):
    """Показать прогресс пользователя"""
    stats = await db.get_user_stats(message.from_user.id)
    lang = stats["user"].get("language", "ru")
    
    user = stats["user"]
    level_title = get_level_title(user["level"])
    
    text = f"""
📊 {user.get('username', 'User')} — {level_title}

⭐ Level: {user["level"]}
💎 XP: {user["xp"]}
🔥 Streak: {user["streak"]} days
📋 Tasks completed: {stats["total_tasks"]}
🏆 Rank: #{stats["rank"]}

📈 Stats by category:
"""
    
    for cat_key, cat_data in stats["stats"].items():
        emoji = CATEGORIES[cat_key]["emoji"]
        name = CATEGORIES[cat_key][f"name_{lang}"]
        text += f"\n{emoji} {name}: {cat_data['xp']} XP ({cat_data['tasks_completed']} tasks)"
    
    await message.answer(text, reply_markup=get_main_menu(lang))

# ========== STREAK ==========
@router.message(F.text.in_([get_text("streak", "ru"), get_text("streak", "uz")]))
async def show_streak(message: Message):
    """Показать streak"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        f"🔥 Текущий streak: {user['streak']} дней\n\n"
        f"Продолжай получать бонусы!\n"
        f"3 дня = +20 XP\n"
        f"7 дней = +50 XP",
        reply_markup=get_main_menu(lang)
    )

# ========== ДОСТИЖЕНИЯ ==========
@router.message(F.text.in_([get_text("achievements", "ru"), get_text("achievements", "uz")]))
async def show_achievements(message: Message):
    """Показать достижения"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        "🏅 Достижения:\n\n"
        "🔥 7 Day Streak\n"
        "📚 First Book\n"
        "💪 10 Workouts\n"
        "🎬 First Skill Task\n"
        "⚡ Level 10\n"
        "🏆 Top 10 Leaderboard\n\n"
        "Скоро будут доступны!",
        reply_markup=get_main_menu(lang)
    )

# ========== ЛИДЕРБОРД ==========
@router.message(F.text.in_([get_text("leaderboard", "ru"), get_text("leaderboard", "uz")]))
async def show_leaderboard(message: Message):
    """Показать таблицу лидеров"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    users = await db.get_leaderboard(10)
    
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 Топ игроков:\n\n"
    
    for i, u in enumerate(users, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        name = u.get('username') or f"User_{u.get('user_id', '???')}"
        text += f"{medal} {name} — Уровень {u['level']} ({u['xp']} XP)\n"
    
    # Добавляем позицию пользователя
    stats = await db.get_user_stats(message.from_user.id)
    text += f"\n📍 Твоя позиция: #{stats['rank']}"
    
    await message.answer(text, reply_markup=get_main_menu(lang))

# ========== ДНЕВНИК ==========
@router.message(F.text.in_([get_text("journal", "ru"), get_text("journal", "uz")]))
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
        await cancel_action(message, state)
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
        await cancel_action(message, state)
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

# ========== НАСТРОЙКИ ==========
@router.message(F.text.in_([get_text("settings", "ru"), get_text("settings", "uz")]))
async def show_settings(message: Message):
    """Показать настройки"""
    user = await db.get_or_create_user(message.from_user.id)
    lang = user.get("language", "ru")
    
    await message.answer(
        f"⚙️ Настройки\n\n"
        f"Текущий язык: {lang.upper()}\n\n"
        f"Выбери язык:",
        reply_markup=get_language_keyboard()
    )

# ========== АДМИН ПАНЕЛЬ ==========
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Админ панель - только для админа"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У тебя нет доступа!")
        return
    
    total = await db.get_all_users_count()
    active = await db.get_active_users_count(7)
    inactive = total - active
    
    await message.answer(
        get_text("admin_panel", "ru", total=total, active=active, inactive=inactive),
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Обновить статистику"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа!")
        return
    
    total = await db.get_all_users_count()
    active = await db.get_active_users_count(7)
    inactive = total - active
    
    await callback.message.edit_text(
        get_text("admin_panel", "ru", total=total, active=active, inactive=inactive),
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_users_all")
async def admin_users_all(callback: CallbackQuery):
    """Показать всех пользователей"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа!")
        return
    
    users = await db.get_users_list(active_only=False, limit=50)
    
    text = get_text("admin_users_list", "ru", filter="все")
    
    for u in users:
        username = u.get('username') or f"ID:{u['user_id']}"
        last_active = u.get('last_active') or "никогда"
        text += f"• {username} | Ур.{u['level']} | {last_active}\n"
    
    if len(text) > 4000:
        text = text[:4000] + "\n\n...и ещё много"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_users_active")
async def admin_users_active(callback: CallbackQuery):
    """Показать активных пользователей"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа!")
        return
    
    users = await db.get_users_list(active_only=True, limit=50)
    
    text = get_text("admin_users_list", "ru", filter="активные 7 дней")
    
    for u in users:
        username = u.get('username') or f"ID:{u['user_id']}"
        text += f"• {username} | Ур.{u['level']} | 🔥{u['streak']}\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_users_inactive")
async def admin_users_inactive(callback: CallbackQuery):
    """Показать неактивных пользователей"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа!")
        return
    
    # Получаем всех и фильтруем неактивных
    all_users = await db.get_users_list(active_only=False, limit=100)
    from datetime import date, timedelta
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    
    inactive_users = [u for u in all_users if (u.get('last_active') or "2000-01-01") < week_ago]
    
    text = get_text("admin_users_list", "ru", filter="неактивные")
    
    for u in inactive_users[:50]:
        username = u.get('username') or f"ID:{u['user_id']}"
        last = u.get('last_active') or "никогда"
        text += f"• {username} | Ур.{u['level']} | {last}\n"
    
    if not inactive_users:
        text += "Нет неактивных пользователей! 🎉"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню из callback"""
    await state.clear()
    user = await db.get_or_create_user(callback.from_user.id)
    lang = user.get("language", "ru")
    
    # Удаляем сообщение с inline клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        get_text("menu", lang),
        reply_markup=get_main_menu(lang)
    )
    await callback.answer()