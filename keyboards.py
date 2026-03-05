from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import TEXTS, CATEGORIES

def get_main_menu(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Главное меню"""
    t = TEXTS[lang]
    
    kb = [
        [KeyboardButton(text=t["start_day"]), KeyboardButton(text=t["add_completion"])],
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
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_delete_tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Клавиатура для удаления задач"""
    buttons = []
    for task in tasks:
        btn = InlineKeyboardButton(
            text=f"🗑 {task['name']}",
            callback_data=f"delete_{task['task_id']}"
        )
        buttons.append([btn])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Кнопка назад"""
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["back"])]],
        resize_keyboard=True
    )

def get_cancel_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Кнопка отмены"""
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["cancel"])]],
        resize_keyboard=True
    )

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Выбор языка"""
    buttons = [
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)