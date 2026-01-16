import aiosqlite


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    grade INTEGER,
                    letter TEXT,
                    reputation INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS homework (
                    id INTEGER PRIMARY KEY,
                    subject_id INTEGER,
                    grade INTEGER,
                    letter TEXT,
                    text TEXT,
                    photo_id TEXT,
                    author_id INTEGER,
                    is_anonymous INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY,
                    homework_id INTEGER,
                    author id INTEGER,
                    text TEXT,
                    photo_id TEXT,
                    is_anonymous INTEGER,
                    FOREIGN KEY (homework_id) REFERENCES homework (id)
                )
                """
            )

            await db.commit()

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

        async with aiosqlite.connect(self.db_path) as db:
            for subject in subjects:
                await db.execute(
                    "INSERT OR IGNORE INTO subjects (name) VALUES (?)", (subject,)
                )
            await db.commit()

    async def register_user(self, user_id, grade, letter):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, grade, letter) VALUES (?, ?, ?)",
                (user_id, grade, letter),
            )
            await db.commit()

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_subjects(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM subjects") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def add_homework(
        self, subject_id, grade, letter, text, photo_id, author_id, is_anonymous
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO homework (subject_id, grade, letter, text, photo_id, author_id, is_anonymous)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (subject_id, grade, letter, text, photo_id, author_id, is_anonymous),
            )
            await db.commit()

    async def get_subject_by_name(self, name):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM subjects WHERE name = ?", (name,)
            ) as cursor:
                return await cursor.fetchone()
