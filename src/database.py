import sqlite3
from datetime import datetime
class Database:
    def __init__(self):
        self.con = sqlite3.connect("workouts.db")
        self.con.execute("PRAGMA foreign_keys = ON")
        self.cur = self.con.cursor()

    def create_tables(self):
        self.cur.executescript("""
                                CREATE TABLE IF NOT EXISTS split_days (
                                split_id INTEGER PRIMARY KEY,
                                name TEXT UNIQUE NOT NULL
                                );
                                
                                CREATE TABLE IF NOT EXISTS exercises (
                                name TEXT NOT NULL,
                                split_id INTEGER NOT NULL,
                                UNIQUE (name, split_id),
                                FOREIGN KEY (split_id)
                                    REFERENCES split_days(split_id)
                                    ON DELETE CASCADE
                                );
                                
                                CREATE TABLE IF NOT EXISTS sessions (
                                session_id INTEGER PRIMARY KEY,
                                split_id INTEGER,
                                performed_at TEXT NOT NULL,
                                FOREIGN KEY (split_id)
                                    REFERENCES split_days(split_id)
                                    ON DELETE SET NULL
                                );
                                
                                CREATE TABLE IF NOT EXISTS sets (
                                set_id INTEGER PRIMARY KEY,
                                session_id INTEGER NOT NULL,
                                name TEXT NOT NULL,
                                weight INTEGER NOT NULL,
                                reps INTEGER NOT NULL,
                                FOREIGN KEY (session_id)
                                    REFERENCES sessions(session_id)
                                    ON DELETE CASCADE
                               );
                                """)
        self.con.commit()
    
    def get_splits(self):
        rows = self.cur.execute("""
                         SELECT * FROM split_days;
                         """).fetchall()
        return [row[:] for row in rows]
    
    def add_workout_split(self, workouts: list):
        for day in workouts:
            self.cur.execute("""
                             INSERT INTO split_days (name)
                             VALUES (?)
                             """, (day,))
        self.con.commit()

    def delete_all_splits(self):
        self.cur.execute("""
                         DELETE FROM split_days;
                         """)
        self.con.commit()
    
    def delete_split(self, split_id: int):
        self.cur.execute("""
                         DELETE FROM split_days
                         WHERE split_id = ?;
                         """, (split_id,))
        self.con.commit()

    def get_all_exercises(self):
        rows = self.cur.execute("""
                                SELECT * FROM exercises;
                                """).fetchall()
        return [row[:] for row in rows]
    
    def get_split_exercises(self, split_id: int):
        rows = self.cur.execute("""
                                SELECT name FROM exercises
                                WHERE split_id = ?
                                """, (split_id,)).fetchall()
        return [row[0] for row in rows]
    
    def add_unique_exercise(self, exercise: str, split_id: int):
        self.cur.execute("""
                         INSERT OR IGNORE INTO exercises (name, split_id)
                         VALUES (?, ?)
                         """, (exercise, split_id))
        self.con.commit()
    
    def add_exercises(self, exercises: list, split_id: int):
        for exercise in exercises:
            self.cur.execute("""
                         INSERT OR IGNORE INTO exercises (name, split_id)
                         VALUES (?, ?)
                         """, (exercise, split_id))
        self.con.commit()

    def delete_exercise(self, name: str, split_id: int):
        self.cur.execute("""
                         DELETE FROM exercises
                         WHERE name = ? AND split_id = ?;  
                        """, (name, split_id))
        self.con.commit()

    def get_sets_logged(self, session_id: int):
        rows = self.cur.execute("""
                                SELECT set_id, name, weight, reps FROM sets
                                WHERE session_id = ?
                                ORDER BY set_id
                                """, (session_id,)).fetchall()
        return [row[:] for row in rows]
    
    def edit_set(self, set_id: int, newweight: int, newreps: int):
        self.cur.execute("""
                            UPDATE sets
                            SET weight = ?,
                            reps = ?
                            WHERE set_id = ?
                        """, (newweight, newreps, set_id))
        self.con.commit()
    
    def delete_set(self, set_id: int):
        self.cur.execute("""
                        DELETE FROM sets
                        WHERE set_id = ?
                        """, (set_id,))
        self.con.commit()
    
    def add_session(self, split_id: int):
        time_logged = datetime.now().isoformat()
        try:   
            self.cur.execute("""
                            INSERT INTO sessions (split_id, performed_at)
                            VALUES (?, ?)
                            """, (split_id, time_logged))
            self.con.commit()
            rows = self.cur.execute("""
                                    SELECT split_days.name, DATE(sessions.performed_at) FROM sessions
                                    JOIN split_days
                                        ON sessions.split_id = split_days.split_id
                                    ORDER BY sessions.performed_at DESC
                                    LIMIT 1;
                                    """).fetchone()
            return [row[:] for row in rows]
        except sqlite3.IntegrityError:
            return None

    #def get_last_session(self):
        #if self.cur.lastrowid():
            #return self.cur.execute("""
                                    #SELECT split_days.name, DATE(sessions.performed_at) FROM sessions
                                    #JOIN split_days
                                        #ON sessions.split_id = split_days.split_id
                                    #ORDER BY sessions.performed_at DESC
                                    #LIMIT 1;
                                    #""").fetchone()
        #return None

    def get_last_session_split_id(self):
        row = self.cur.execute("""
                                SELECT split_id FROM sessions
                                ORDER BY session_id DESC
                                LIMIT 1
                                """).fetchone()
        return row[0] if row else None

    def get_last_session_id(self):
        row = self.cur.execute("""
                                SELECT MAX(session_id) FROM sessions
                                """).fetchone()
        return row[0]
        
    
    def delete_session(self, session_id: int):
        self.cur.execute("""
                         DELETE FROM sessions
                         WHERE session_id = ?;
                         """, (session_id,))
        self.con.commit()

    def add_set(self, session_id: int, name: str, weight: int, reps: int):
        self.cur.execute("""
                         INSERT INTO sets (session_id, name, weight, reps)
                         VALUES (?, ?, ?, ?)
                         """, (session_id, name, weight, reps))
        self.con.commit()

    def delete_set(self, set_id: int):
        self.cur.execute("""
                         DELETE FROM sets
                         WHERE set_id = ?;
                         """, (set_id,))
        self.con.commit()