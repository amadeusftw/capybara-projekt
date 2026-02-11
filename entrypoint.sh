#!/bin/bash
set -e

echo "🚀 Starting application initialization..."

# 1. Initiera databasen (Säkerställer att tabellerna finns)
echo "Initializing database..."
cd /code
# Vi kör en python-snutt för att skapa tabellerna direkt
python -c "from app.app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized.')"

# 2. Skapa Admin-användare (Om variabler finns i Azure)
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "👤 Seeding admin user..."
    python -c "
import os
from app.app import app, db
from app.models import User
from werkzeug.security import generate_password_hash

username = os.environ.get('ADMIN_USERNAME')
password = os.environ.get('ADMIN_PASSWORD')

with app.app_context():
    # Kolla om admin redan finns
    existing_user = User.query.filter_by(username=username).first()
    if not existing_user:
        # Skapa ny admin (hårdkodat ID 1 eller auto)
        user = User(username=username, is_admin=True)
        user.set_password(password) # Antar att du har denna metod, annars: user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        print(f'✅ Admin {username} created successfully!')
    else:
        print(f'ℹ️ Admin {username} already exists. Skipping.')
"
else
    echo "⚠️ Warning: ADMIN_USERNAME or ADMIN_PASSWORD not set in Azure. Skipping admin seeding."
fi

# 3. Starta Gunicorn
# VIKTIGT: Vi pekar på app.app:app (Mappen app -> filen app.py -> variabeln app)
echo "🔥 Starting gunicorn server on port 5000..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app.app:app