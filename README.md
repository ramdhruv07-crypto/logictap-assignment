# Logictap call-ended service

Flask + SQLite. POST /call-ended stores a call once (repeats return 200, no second record). GET /calls/<call_id> returns it or 404.

Run: pip install flask, then python app.py
Test: python -m unittest test_app -v

v1_app.py is the first draft. app.py is the final version.
