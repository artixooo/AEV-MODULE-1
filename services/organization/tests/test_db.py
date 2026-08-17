import unittest
from app.db.database import Base, SessionLocal, engine, get_db


class TestDatabase(unittest.TestCase):
    def test_db_setup(self):
        self.assertIsNotNone(engine)
        self.assertIsNotNone(SessionLocal)
        self.assertIsNotNone(Base)

    def test_get_db_generator(self):
        db_gen = get_db()
        self.assertIsNotNone(db_gen)
        session_item = next(db_gen)
        self.assertIsNotNone(session_item)
        try:
            next(db_gen)
        except StopIteration:
            pass


if __name__ == "__main__":
    unittest.main()
