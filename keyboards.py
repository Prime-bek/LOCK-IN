from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import TEXTS, CATEGORIES

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Выбор языка при первом входе"""
    buttons = [
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Главное меню"""
    t = TEXTS[lang]
    
    kb = [
        [KeyboardButton(text=t["start_day"])],
        [KeyboardButton(text=t["my_tasks"]), KeyboardButton(text=t["add_task"])],
        [KeyboardButton(text=t["progress"]), KeyboardButton(text=t["leaderboard"])],
        [KeyboardButton(text=t["streak"]), KeyboardButton(text=t["achievements"])],
        [KeyboardButton(text=t["journal"]), KeyboardButton(text=t["settings"])]
    ]
    
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_categories_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора категории"""
    buttons = []
    for key, value in CATEGORIES.items():
        name = value[f"name_{lang}"]
        btn = InlineKeyboardButton(
            text=f"{value['emoji']} {name}",
            callback_data=f"cat_{key}"
        )
        buttons.append([btn])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tasks_keyboard(tasks: list, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура со списком задач для выполнения"""
    buttons = []
    for task in tasks:
        emoji = CATEGORIES.get(task['category'], {}).get('emoji', '✅')
        btn = InlineKeyboardButton(
            text=f"{emoji} {task['name']} (+{task['xp']} XP)",
            callback_data=f"complete_{task['task_id']}"
        )
        buttons.append([btn])
    
    # Кнопка назад
    t = TEXTS[lang]
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_delete_tasks_keyboard(tasks: list, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для удаления задач"""
    buttons = []
    for task in tasks:
        btn = InlineKeyboardButton(
            text=f"🗑 {task['name']}",
            callback_data=f"delete_{task['task_id']}"
        )
        buttons.append([btn])
    
    t = TEXTS[lang]
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Кнопка отмены"""
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["cancel"])]],
        resize_keyboard=True
    )

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Админ-панель"""
    buttons = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Все пользователи", callback_data="admin_users_all")],
        [InlineKeyboardButton(text="⚡ Активные (7 дней)", callback_data="admin_users_active")],
        [InlineKeyboardButton(text="😴 Неактивные", callback_data="admin_users_inactive")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_button(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка назад для inline"""
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t["back"], callback_data="back_to_menu")]]
    )