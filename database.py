from typing import Any, List, Dict, Optional, Union
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

    async def create_tables(self):
        # Создание всех таблиц одним методом
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                grade INTEGER,
                letter TEXT,
                reputation INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
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
                photo_id TEXT,
                is_anonymous INTEGER,
                FOREIGN KEY (homework_id) REFERENCES homework (id)
            )""",
            """
            CREATE TABLE IF NOT EXISTS votes (
                user_id INTEGER,
                solution_id INTEGER,
                vote_value INTEGER,
                PRIMARY KEY (user_id, solution_id)
            )""",
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

    # --- Работа с предметами ---
    async def get_subjects(self):
        return await self._execute("SELECT * FROM subjects", fetch=True)

    async def get_subject_by_name(self, name):
        return await self._execute(
            "SELECT * FROM subjects WHERE name = ?", (name,), fetchone=True
        )

    # --- Работа с домашкой ---
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

    # --- Работа с решениями ---
    async def add_solution(self, hw_id, author_id, text, photo_id, is_anonymous):
        query = "INSERT INTO solutions (homework_id, author_id, text, photo_id, is_anonymous) VALUES (?, ?, ?, ?, ?)"
        await self._execute(query, (hw_id, author_id, text, photo_id, is_anonymous))

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
        ups = await self._execute(
            "SELECT COUNT(*) as count FROM votes WHERE solution_id = ? AND vote_type = 1",
            (sol_id,),
            fetchone=True,
        )
        downs = await self._execute(
            "SELECT COUNT(*) as count FROM votes WHERE solution_id = ? AND vote_type = -1",
            (sol_id,),
            fetchone=True,
        )
        return ups["count"], downs["count"]
