import sqlite3
import tempfile
import os
import unittest

from app import create_app


class DuplicateTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.client = create_app(self.db_path).test_client()

    def tearDown(self):
        os.remove(self.db_path)

    def test_repeated_request_does_not_create_second_record(self):
        body = {"call_id": "abc123", "status": "answered", "duration_secs": 42}

        first = self.client.post("/call-ended", json=body)
        second = self.client.post("/call-ended", json=body)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)  # still success

        conn = sqlite3.connect(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM calls WHERE call_id = 'abc123'").fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    def test_missing_call_id_is_rejected(self):
        resp = self.client.post("/call-ended", json={"status": "answered"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("call_id", resp.get_json()["error"])

    def test_unknown_call_is_404(self):
        self.assertEqual(self.client.get("/calls/nope").status_code, 404)


if __name__ == "__main__":
    unittest.main()
