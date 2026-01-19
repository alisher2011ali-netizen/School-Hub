from typing import Any, List, Dict, Optional, Union
from datetime import datetime
import aiosqlite


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    # --- Приватный метод-движок для сокращения кода ---
    async def _execute(
        self,
        query: str,
        params: tuple = (),
        fetch: bool = False,
        fetchone: bool = False,
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None, aiosqlite.Cursor]:

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)

            if fetchone:
                row = await cursor.fetchone()
                return dict(row) if row else None

            if fetch:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

            await db.commit()
            return cursor

    # --- Создание всех таблиц в базе даных ---
    async def create_tables(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                grade INTEGER,
                letter TEXT,
                reputation INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )""",
            """CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY,
                subject_id INTEGER,
                grade INTEGER,
                letter TEXT,
                text TEXT,
                photo_id TEXT,
                author_id INTEGER,
                target_date TEXT,
                is_anonymous INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )""",
            """CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY,
                homework_id INTEGER,
                author_id INTEGER,
                text TEXT,
                is_anonymous INTEGER,
                FOREIGN KEY (homework_id) REFERENCES homework (id) ON DELETE CASCADE
            )""",
            """
            CREATE TABLE IF NOT EXISTS votes (
                user_id INTEGER,
                solution_id INTEGER,
                vote_value INTEGER,
                PRIMARY KEY (user_id, solution_id)
            )""",
            """
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER,
                parent_type TEXT,
                file_id TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER,
                target_id INTEGER,
                type TEXT,
                sol_or_hw_id INTEGER,
                reason TEXT,
                status TEXT DEFAULT 'open'
            )
            """,
        ]
        for query in queries:
            await self._execute(query)

    async def seed_subjects(self):
        subjects = [
            "Алгебра",
            "Геометрия",
            "Вероятность и статистика",
            "Информатика",
            "Программирование",
            "Физика",
            "Русский язык",
            "Литература",
            "История",
            "Обществознание",
            "Английский язык",
            "Химия",
            "Биология",
            "География",
            "Физкультура",
            "ОБЗиР",
            "Искусство",
        ]
        for subject in subjects:
            await self._execute(
                "INSERT OR IGNORE INTO subjects (name) VALUES (?)", (subject,)
            )

    # --- Работа с пользователями ---
    async def register_user(self, user_id, first_name, last_name, grade, letter):
        await self._execute(
            "INSERT OR IGNORE INTO users (user_id, first_name, last_name, grade, letter) VALUES (?, ?, ?, ?, ?)",
            (user_id, first_name, last_name, grade, letter),
        )

    async def get_user(self, user_id):
        return await self._execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,), fetchone=True
        )

    async def update_reputation(self, user_id, value):
        await self._execute(
            "UPDATE users SET reputation = reputation + ? WHERE user_id = ?",
            (value, user_id),
        )

    async def get_top_users(self, limit: int = 5):
        query = """
            SELECT first_name, last_name, grade, letter, reputation
            FROM users
            ORDER BY reputation DESC
            LIMIT ?
        """
        return await self._execute(query, (limit,), fetch=True)

    async def get_class_users(self, grade: int, letter: str):
        query = """
            SELECT first_name, last_name, reputation
            FROM users
            WHERE grade = ? AND letter = ?
            ORDER BY reputation DESC
        """
        return await self._execute(query, (grade, letter), fetch=True)

    async def ban_user(self, user_id):
        await self._execute(
            "UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,)
        )

    async def unban_user(self, user_id):
        await self._execute(
            "UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,)
        )

    async def set_admin_status(self, user_id, status):
        await self._execute(
            "UPDATE users SET is_admin = ? WHERE user_id = ?", (status, user_id)
        )

    # --- Работа с предметами ---
    async def get_subjects(self):
        return await self._execute("SELECT * FROM subjects", fetch=True)

    async def get_subject_by_name(self, name):
        return await self._execute(
            "SELECT * FROM subjects WHERE name = ?", (name,), fetchone=True
        )

    # --- Работа с домашкой ---
    async def delete_expired_homework(self):
        today = datetime.now().strftime("%Y-%m-%d")
        await self._execute(
            """
                    DELETE FROM media 
                    WHERE parent_type = 'solution' 
                    AND parent_id IN (SELECT id FROM solutions WHERE homework_id IN (SELECT id FROM homework WHERE target_date < ?))
                """,
            (today,),
        )
        query = "DELETE FROM homework WHERE target_date < ?"
        await self._execute(query, (today,))

    async def add_homework(
        self,
        subject_id,
        grade,
        letter,
        text,
        photo_id,
        target_date,
        author_id,
        is_anonymous,
    ):
        query = """INSERT INTO homework (subject_id, grade, letter, text, photo_id, target_date, author_id, is_anonymous)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        params = (
            subject_id,
            grade,
            letter,
            text,
            photo_id,
            target_date,
            author_id,
            is_anonymous,
        )
        await self._execute(query, params)

    async def get_homework_by_class(self, grade, letter):
        query = """SELECT h.*, s.name as subject_name FROM homework h
                   JOIN subjects s ON h.subject_id = s.id
                   WHERE h.grade = ? AND h.letter = ?
                   ORDER BY h.target_date ASC, h.created_at DESC"""
        return await self._execute(query, (grade, letter), fetch=True)

    async def get_homework_by_id(self, hw_id):
        return await self._execute("SELECT * FROM homework WHERE id = ?", (hw_id,))

    # --- Работа с решениями ---
    async def add_solution(self, homework_id, author_id, text, is_anonymous):
        query = "INSERT INTO solutions (homework_id, author_id, text, is_anonymous) VALUES (?, ?, ?, ?)"
        cursor = await self._execute(
            query, (homework_id, author_id, text, is_anonymous)
        )
        return cursor.lastrowid

    async def get_solutions(self, hw_id):
        return await self._execute(
            "SELECT * FROM solutions WHERE homework_id = ?", (hw_id,), fetch=True
        )

    async def check_solution_exists(self, hw_id):
        res = await self._execute(
            "SELECT COUNT(*) as count FROM solutions WHERE homework_id = ?",
            (hw_id,),
            fetchone=True,
        )
        return res["count"] > 0 if res else False

    async def get_solution_by_id(self, sol_id):
        return await self._execute(
            "SELECT * FROM solutions WHERE id = ?", (sol_id,), fetchone=True
        )

    # --- Работа с медиа ---
    async def add_solution_media(
        self,
        solution_id: int,
        file_id: str,
    ):
        query = "INSERT INTO media (parent_id, parent_type, file_id) VALUES (?, 'solution', ?)"
        await self._execute(
            query,
            (
                solution_id,
                file_id,
            ),
        )

    async def get_media(self, parent_id: int, parent_type: str):
        query = "SELECT file_id FROM media WHERE parent_id = ?AND parent_type = ?"
        return await self._execute(query, (parent_id, parent_type), fetch=True)

    # --- Работа с голосами ---
    async def add_vote(self, user_id, sol_id, vote_value):
        try:
            await self._execute(
                "INSERT INTO votes (user_id, solution_id, vote_value) VALUES (?, ?, ?)",
                (user_id, sol_id, vote_value),
            )
            return True
        except:
            return False

    async def get_solution_votes(self, sol_id):
        query = """
            SELECT
                SUM(CASE WHEN vote_value = 1 THEN 1 ELSE 0 END) as ups,
                SUM(CASE WHEN vote_value = -1 THEN 1 ELSE 0 END) as downs
            FROM votes
            WHERE solution_id = ?
        """
        res = await self._execute(query, (sol_id,), fetchone=True)

        ups = res["ups"] if res and res["ups"] else 0
        downs = res["downs"] if res and res["downs"] else 0

        return ups, downs

    async def add_report(
        self,
        reporter_id: int,
        target_id: int,
        type: str,
        sol_or_hw_id: int,
        reason: str,
    ):
        query = """
            INSERT INTO reports (
                reporter_id, target_id, type, sol_or_hw_id, reason
                )
            VALUES (?, ?, ?, ?, ?)
        """
        await self._execute(query, (reporter_id, target_id, type, sol_or_hw_id, reason))
