from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

from handball.infrastructure.database.models.base import Baza

baza_danych = SQLAlchemy(model_class=Baza)
