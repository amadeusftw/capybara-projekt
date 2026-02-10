# En enkel lista som agerar databas just nu
import time
subscribers = [
    {
        "first_name": "Anna",
        "last_name": "Andersson",
        "email": "anna@example.com",
        "company": "TechAB",
        "title": "VD",
        "created_at": int(time.time()) - 3000
    },
    {
        "first_name": "Lars",
        "last_name": "Larsson",
        "email": "lars@example.com",
        "company": "Bilar & Co",
        "title": "Mekaniker",
        "created_at": int(time.time()) - 2000
    },
    {
        "first_name": "Karin",
        "last_name": "Karlsson",
        "email": "karin@example.com",
        "company": "Byggmax",
        "title": "Säljare",
        "created_at": int(time.time()) - 1000
    }
]