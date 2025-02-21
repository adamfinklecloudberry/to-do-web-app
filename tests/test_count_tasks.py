"""Tests for counting the number of tasks"""

import pytest
from flask import url_for
from tests.helpers import insert_task, add_test_user, login_test_user


def test_count_tasks(client):
    """Tests whether the number of tasks returned is correct"""
    insert_task("Test task", "2023-01-01")
    add_test_user()
    login_test_user(client)
    response = client.get(url_for("home.home"))
    assert b"Number of tasks: 1" in response.data
