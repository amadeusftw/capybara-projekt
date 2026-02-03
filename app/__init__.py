import os
from typing import Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Vi importerar config-inställningarna vi skapade i steg 2
from .config import config

# --- HÄR ÄR DET VIKTIGA TILLÄGGET ---
# Skapa extension-objekten utanför funktionen (Module level)
db = SQLAlchemy()


def create_app(config_name: Optional[str] = None) -> Flask:
    # Om ingen config anges, använd 'development' som standard
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="presentation/templates",
        static_folder="presentation/static",
    )

    # Ladda inställningar från config.py (Där databas-URL och secret key finns)
    # Om config-nyckeln finns, ladda den
    if config_name in config:
        app.config.from_object(config[config_name])

    # --- FIX: SÄKERSTÄLL ATT DATABASEN HITTAS ---
    # Om config-filen inte laddades korrekt eller saknar URI, använder vi denna som backup
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

    # --- INITIALISERA DATABASEN ---
    # Koppla ihop db med just denna app-instans
    db.init_app(app)

    # Importera modeller 
    # (Vi gör detta efter db.init_app för att undvika cirkulära import-fel)
    from .data import models  # noqa: F401

    # --- REGISTRERA RUTTER ---
    
    # Public
    from .presentation.routes.public import bp as public_bp
    app.register_blueprint(public_bp)

    # Admin
    from .presentation.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app