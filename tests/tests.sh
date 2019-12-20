#!/bin/bash
python3 tests/pr_approved.py
python3 tests/pr_comment.py
python3 tests/pr_edited.py
python3 tests/pr_open_body.py
python3 tests/pr_request_changes.py
python3 tests/pr_review_comment.py
python3 tests/review_requested.py