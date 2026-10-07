"""
SQLite ma'lumotlar bazasi moduli.
Foydalanuvchilar, savollar bazasi, progress va Socratic sessiyalarni boshqaradi.
"""
import sqlite3
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from config import DATABASE_PATH
from core.models import Question, ProgressReport

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Foydalanuvchilar jadvali
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                selected_subject TEXT DEFAULT 'Matematika',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Savollar jadvali
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_text TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                formula_or_expr TEXT,
                explanation_steps TEXT NOT NULL,
                verified INTEGER DEFAULT 1,
                source TEXT DEFAULT 'DTM_baza'
            )
            """)

            # Foydalanuvchi javoblari (Progress)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            )
            """)

            # Socratic sessiyalar jadvali ("Tushunmadim" so'rovlari uchun)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS socratic_sessions (
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                request_count INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, question_id)
            )
            """)

            # Kunlik rejalar jadvali
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_date TEXT NOT NULL,
                topic TEXT NOT NULL,
                target_count INTEGER NOT NULL,
                solved_count INTEGER DEFAULT 0
            )
            """)

            conn.commit()

    # --- Foydalanuvchi metodlari ---
    def get_or_create_user(self, user_id: int, full_name: str = "", username: str = "") -> dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            cursor.execute(
                "INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
                (user_id, full_name, username)
            )
            conn.commit()
            return {"user_id": user_id, "full_name": full_name, "username": username, "selected_subject": "Matematika"}

    def set_user_subject(self, user_id: int, subject: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET selected_subject = ? WHERE user_id = ?", (subject, user_id))
            conn.commit()

    def get_user_subject(self, user_id: int) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT selected_subject FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row["selected_subject"] if row and row["selected_subject"] else "Matematika"

    def clear_questions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM questions")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'questions'")
            conn.commit()

    def add_question(self, q: dict) -> int:
        options_json = json.dumps(q["options"], ensure_ascii=False)
        steps_json = json.dumps(q.get("explanation_steps", []), ensure_ascii=False)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO questions (subject, topic, difficulty, question_text, options, correct_option, formula_or_expr, explanation_steps, verified, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["subject"],
                q["topic"],
                q.get("difficulty", "medium"),
                q["question_text"],
                options_json,
                q["correct_option"],
                q.get("formula_or_expr", ""),
                steps_json,
                1 if q.get("verified", True) else 0,
                q.get("source", "DTM_baza")
            ))
            conn.commit()
            return cursor.lastrowid

    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Question(
                id=row["id"],
                subject=row["subject"],
                topic=row["topic"],
                difficulty=row["difficulty"],
                question_text=row["question_text"],
                options=json.loads(row["options"]),
                correct_option=row["correct_option"],
                formula_or_expr=row["formula_or_expr"],
                explanation_steps=json.loads(row["explanation_steps"]),
                verified=bool(row["verified"]),
                source=row["source"]
            )

    def get_questions_by_filter(
        self,
        subject: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 1,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Question]:
        query = "SELECT * FROM questions WHERE subject = ?"
        params: List[Any] = [subject]

        if topic:
            query += " AND topic = ?"
            params.append(topic)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        if exclude_ids and len(exclude_ids) > 0:
            placeholders = ",".join("?" for _ in exclude_ids)
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)

        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Question(
                    id=row["id"],
                    subject=row["subject"],
                    topic=row["topic"],
                    difficulty=row["difficulty"],
                    question_text=row["question_text"],
                    options=json.loads(row["options"]),
                    correct_option=row["correct_option"],
                    formula_or_expr=row["formula_or_expr"],
                    explanation_steps=json.loads(row["explanation_steps"]),
                    verified=bool(row["verified"]),
                    source=row["source"]
                )
                for row in rows
            ]

    def count_questions(self, subject: Optional[str] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if subject:
                cursor.execute("SELECT COUNT(*) FROM questions WHERE subject = ?", (subject,))
            else:
                cursor.execute("SELECT COUNT(*) FROM questions")
            return cursor.fetchone()[0]

    # --- Progress va tahlil metodlari ---
    def record_answer(self, user_id: int, question_id: int, subject: str, topic: str, is_correct: bool, user_answer: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO progress (user_id, question_id, subject, topic, is_correct, user_answer)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, question_id, subject, topic, 1 if is_correct else 0, user_answer))
            conn.commit()

    def get_user_topic_stats(self, user_id: int, subject: str) -> Dict[str, Dict[str, Any]]:
        """Mavzular bo'yicha foydalanuvchining to'g'ri/noto'g'ri ko'rsatkichlari."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT topic,
                   COUNT(*) as total,
                   SUM(is_correct) as correct
            FROM progress
            WHERE user_id = ? AND subject = ?
            GROUP BY topic
            """, (user_id, subject))
            rows = cursor.fetchall()
            result = {}
            for r in rows:
                total = r["total"]
                correct = r["correct"] or 0
                acc = (correct / total) if total > 0 else 0.0
                result[r["topic"]] = {
                    "total": total,
                    "correct": correct,
                    "accuracy": acc
                }
            return result

    def get_user_recent_mistakes(self, user_id: int, subject: str, limit: int = 5) -> List[int]:
        """Oxirgi noto'g'ri ishlangan savollar ID ro'yxati."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT question_id FROM progress
            WHERE user_id = ? AND subject = ? AND is_correct = 0
            ORDER BY id DESC LIMIT ?
            """, (user_id, subject, limit))
            return [row["question_id"] for row in cursor.fetchall()]

    def get_user_solved_ids(self, user_id: int, subject: str) -> List[int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT question_id FROM progress WHERE user_id = ? AND subject = ?", (user_id, subject))
            return [row["question_id"] for row in cursor.fetchall()]

    def get_progress_summary(self, user_id: int, period: str = "week") -> Dict[str, Any]:
        """Hafta yoki oy bo'yicha progress statistikasi."""
        now = datetime.now()
        if period == "week":
            start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
        elif period == "month":
            start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
        else:
            start_date = "2000-01-01 00:00:00"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT COUNT(*) as total, SUM(is_correct) as correct
            FROM progress
            WHERE user_id = ? AND timestamp >= ?
            """, (user_id, start_date))
            summary_row = cursor.fetchone()
            total = summary_row["total"] or 0
            correct = summary_row["correct"] or 0

            # Kunlik tahlil (grafik chizish uchun)
            cursor.execute("""
            SELECT date(timestamp) as p_date,
                   COUNT(*) as total,
                   SUM(is_correct) as correct
            FROM progress
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY date(timestamp)
            ORDER BY p_date ASC
            """, (user_id, start_date))
            daily_rows = cursor.fetchall()
            daily_data = [
                {"date": r["p_date"], "total": r["total"], "correct": r["correct"] or 0}
                for r in daily_rows
            ]

            return {
                "total": total,
                "correct": correct,
                "accuracy": (correct / total) if total > 0 else 0.0,
                "daily": daily_data
            }

    # --- Socratic Session ---
    def get_socratic_count(self, user_id: int, question_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT request_count FROM socratic_sessions WHERE user_id = ? AND question_id = ?", (user_id, question_id))
            row = cursor.fetchone()
            return row["request_count"] if row else 0

    def increment_socratic_count(self, user_id: int, question_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT request_count FROM socratic_sessions WHERE user_id = ? AND question_id = ?", (user_id, question_id))
            row = cursor.fetchone()
            if row:
                new_count = row["request_count"] + 1
                cursor.execute(
                    "UPDATE socratic_sessions SET request_count = ?, last_updated = CURRENT_TIMESTAMP WHERE user_id = ? AND question_id = ?",
                    (new_count, user_id, question_id)
                )
            else:
                new_count = 1
                cursor.execute(
                    "INSERT INTO socratic_sessions (user_id, question_id, request_count) VALUES (?, ?, ?)",
                    (user_id, question_id, new_count)
                )
            conn.commit()
            return new_count

    # --- Kunlik reja ---
    def get_today_plan(self, user_id: int, today_str: Optional[str] = None) -> List[Dict[str, Any]]:
        date_str = today_str or date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_plans WHERE user_id = ? AND plan_date = ?", (user_id, date_str))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def set_today_plan(self, user_id: int, items: List[Dict[str, Any]], today_str: Optional[str] = None):
        date_str = today_str or date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_plans WHERE user_id = ? AND plan_date = ?", (user_id, date_str))
            for item in items:
                cursor.execute("""
                INSERT INTO daily_plans (user_id, plan_date, topic, target_count, solved_count)
                VALUES (?, ?, ?, ?, ?)
                """, (user_id, date_str, item["topic"], item["target_count"], item.get("solved_count", 0)))
            conn.commit()

    def update_plan_progress(self, user_id: int, topic: str, today_str: Optional[str] = None):
        date_str = today_str or date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE daily_plans
            SET solved_count = solved_count + 1
            WHERE user_id = ? AND plan_date = ? AND topic = ?
            """, (user_id, date_str, topic))
            conn.commit()

db = Database()
