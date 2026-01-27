from flask import Flask

def create_app(config_name=None):
    # Skapa appen
    app = Flask(__name__, 
                template_folder="presentation/templates", 
                static_folder="presentation/static")

    # --- NÖDLÖSNING ---
    # Vi hårdkodar nyckeln så att sessions-hanteringen (inloggningen) GARANTERAT funkar
    app.secret_key = "detta_ar_en_mycket_hemlig_nyckel_123"
    
    # Vi slår på DEBUG-läge. 
    # Detta gör att om något kraschar får du en detaljerad rapport i webbläsaren 
    # istället för bara "Internal Server Error".
    app.debug = True

    # Registrera PUBLIC rutter
    from .presentation.routes.public import bp as public_bp
    app.register_blueprint(public_bp)

    # Registrera ADMIN rutter
    from .presentation.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app