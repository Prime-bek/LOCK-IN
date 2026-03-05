import aiosqlite
import datetime
from typing import Optional, List, Dict, Any
from config import DB_PATH, CATEGORIES

class Database:
    def __init__(self):
        self.db_path = DB_PATH
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Пользователи
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    language TEXT DEFAULT 'ru',
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    streak INTEGER DEFAULT 0,
                    last_active DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Статистика по категориям
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER,
                    category TEXT,
                    xp INTEGER DEFAULT 0,
                    tasks_completed INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, category),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Задачи (шаблоны)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    category TEXT,
                    xp INTEGER,
                    is_daily BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Выполненные задачи
            await db.execute('''
                CREATE TABLE IF NOT EXISTS completed_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_id INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    xp_earned INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                )
            ''')
            
            # Дневник
            await db.execute('''
                CREATE TABLE IF NOT EXISTS journal (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    q1 TEXT,
                    q2 TEXT,
                    created_at DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Достижения
            await db.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            await db.commit()
    
    async def get_or_create_user(self, user_id: int, username: str = None) -> Dict:
        """Получить или создать пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                user = await cursor.fetchone()
            
            if not user:
                today = datetime.date.today().isoformat()
                await db.execute(
                    "INSERT INTO users (user_id, username, last_active) VALUES (?, ?, ?)",
                    (user_id, username, today)
                )
                await db.commit()
                
                # Создаем начальные статы
                for cat in CATEGORIES.keys():
                    await db.execute(
                        "INSERT INTO user_stats (user_id, category, xp) VALUES (?, ?, 0)",
                        (user_id, cat)
                    )
                await db.commit()
                
                async with db.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                ) as cursor:
                    user = await cursor.fetchone()
            
            return dict(user)
    
    async def add_xp(self, user_id: int, xp: int, category: str = None) -> Dict[str, Any]:
        """Добавить XP пользователю"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем текущие данные
            async with db.execute(
                "SELECT xp, level FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                user = await cursor.fetchone()
            
            current_xp, current_level = user
            new_xp = current_xp + xp
            new_level = current_level
            
            # Проверяем повышение уровня (каждые 100 XP)
            while new_xp >= new_level * 100:
                new_level += 1
            
            # Обновляем пользователя
            await db.execute(
                "UPDATE users SET xp = ?, level = ? WHERE user_id = ?",
                (new_xp, new_level, user_id)
            )
            
            # Обновляем статы категории
            if category:
                await db.execute('''
                    INSERT INTO user_stats (user_id, category, xp, tasks_completed)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(user_id, category) 
                    DO UPDATE SET xp = xp + ?, tasks_completed = tasks_completed + 1
                ''', (user_id, category, xp, xp))
            
            await db.commit()
            
            return {
                "old_level": current_level,
                "new_level": new_level,
                "leveled_up": new_level > current_level,
                "total_xp": new_xp
            }
    
    async def create_task(self, user_id: int, name: str, category: str, xp: int, is_daily: bool = False) -> int:
        """Создать задачу"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO tasks (user_id, name, category, xp, is_daily) VALUES (?, ?, ?, ?, ?)",
                (user_id, name, category, xp, is_daily)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_user_tasks(self, user_id: int) -> List[Dict]:
        """Получить задачи пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """Удалить задачу"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM tasks WHERE task_id = ? AND user_id = ?",
                (task_id, user_id)
            )
            await db.commit()
            return True
    
    async def complete_task(self, user_id: int, task_id: int) -> Dict:
        """Выполнить задачу и начислить XP"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем информацию о задаче
            async with db.execute(
                "SELECT * FROM tasks WHERE task_id = ? AND user_id = ?",
                (task_id, user_id)
            ) as cursor:
                task = await cursor.fetchone()
            
            if not task:
                return None
            
            task = dict(task)
            
            # Записываем выполнение
            await db.execute(
                "INSERT INTO completed_tasks (user_id, task_id, xp_earned) VALUES (?, ?, ?)",
                (user_id, task_id, task['xp'])
            )
            
            await db.commit()
            
            # Начисляем XP
            result = await self.add_xp(user_id, task['xp'], task['category'])
            result['task_name'] = task['name']
            result['xp'] = task['xp']
            
            return result
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Получить полную статистику пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Основная инфо
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                user = dict(await cursor.fetchone())
            
            # Статистика по категориям
            async with db.execute(
                "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
            ) as cursor:
                stats = {row['category']: dict(row) for row in await cursor.fetchall()}
            
            # Всего выполнено задач
            async with db.execute(
                "SELECT COUNT(*) as count FROM completed_tasks WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                total_tasks = (await cursor.fetchone())['count']
            
            # Позиция в рейтинге
            async with db.execute(
                "SELECT COUNT(*) as rank FROM users WHERE xp > ?",
                (user['xp'],)
            ) as cursor:
                rank = (await cursor.fetchone())['rank'] + 1
            
            return {
                "user": user,
                "stats": stats,
                "total_tasks": total_tasks,
                "rank": rank
            }
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Получить топ пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT username, level, xp FROM users ORDER BY xp DESC LIMIT ?",
                (limit,)
            ) as cursor:
                return [dict(row) for row in await cursor.fetchall()]
    
    async def save_journal_entry(self, user_id: int, q1: str, q2: str):
        """Сохранить запись дневника"""
        async with aiosqlite.connect(self.db_path) as db:
            today = datetime.date.today().isoformat()
            await db.execute(
                "INSERT INTO journal (user_id, q1, q2, created_at) VALUES (?, ?, ?, ?)",
                (user_id, q1, q2, today)
            )
            await db.commit()
    
    async def update_streak(self, user_id: int) -> Dict:
        """Обновить streak пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            today = datetime.date.today()
            
            async with db.execute(
                "SELECT last_active, streak FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
            
            last_active = datetime.date.fromisoformat(row['last_active']) if row['last_active'] else None
            current_streak = row['streak'] or 0
            
            if last_active:
                diff = (today - last_active).days
                
                if diff == 0:
                    # Уже активен сегодня
                    return {"streak": current_streak, "bonus": 0, "message": None}
                elif diff == 1:
                    # Продолжаем streak
                    new_streak = current_streak + 1
                    bonus = 0
                    message = None
                    
                    if new_streak == 3:
                        bonus = 20
                        message = "streak_3"
                    elif new_streak == 7:
                        bonus = 50
                        message = "streak_7"
                    elif new_streak == 30:
                        message = "streak_30"
                    
                    await db.execute(
                        "UPDATE users SET streak = ?, last_active = ? WHERE user_id = ?",
                        (new_streak, today.isoformat(), user_id)
                    )
                    await db.commit()
                    
                    return {"streak": new_streak, "bonus": bonus, "message": message}
                else:
                    # Streak сброшен
                    await db.execute(
                        "UPDATE users SET streak = 1, last_active = ? WHERE user_id = ?",
                        (today.isoformat(), user_id)
                    )
                    await db.commit()
                    return {"streak": 1, "bonus": 0, "message": "broken", "old_streak": current_streak}
            else:
                # Первый день
                await db.execute(
                    "UPDATE users SET streak = 1, last_active = ? WHERE user_id = ?",
                    (today.isoformat(), user_id)
                )
                await db.commit()
                return {"streak": 1, "bonus": 0, "message": None}

# Глобальный экземпляр базы данных
db = Database()