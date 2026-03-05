from config import LEVELS, TEXTS

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

def format_progress(stats: dict, lang: str = "ru") -> str:
    """Форматировать статистику прогресса"""
    t = TEXTS[lang]
    user = stats["user"]
    categories = stats["stats"]
    
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
    
    for cat_key, cat_data in categories.items():
        from config import CATEGORIES
        emoji = CATEGORIES[cat_key]["emoji"]
        name = CATEGORIES[cat_key][f"name_{lang}"]
        text += f"\n{emoji} {name}: {cat_data['xp']} XP ({cat_data['tasks_completed']} tasks)"
    
    return text

def format_leaderboard(users: list, lang: str = "ru") -> str:
    """Форматировать таблицу лидеров"""
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 Global Leaderboard\n\n"
    
    for i, user in enumerate(users[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        name = user.get('username') or f"User_{user.get('user_id', '???')}"
        text += f"{medal} {name} — Level {user['level']} ({user['xp']} XP)\n"
    
    return text