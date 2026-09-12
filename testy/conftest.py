from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from pilka_reczna import create_app


@pytest.fixture()
def aplikacja() -> Flask:
    return create_app()


@pytest.fixture()
def klient(aplikacja: Flask) -> FlaskClient:
    return aplikacja.test_client()
