import os
import urllib.request

print("### HÄMTAR TILLBAKA CAPYBARAN... ###")

# 1. Definiera vart bilden ska bo (Vi rör INGA andra mappar)
static_folder = "app/static"

# Skapa mappen om den mot förmodan saknas
os.makedirs(static_folder, exist_ok=True)

# 2. Länken till en bra Capybara-gif
image_url = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYzJqaWF4cTU3a2I4aW41aW41aW41aW41aW41aW41aW41/HiMfr4FyhaURlMQGiF/giphy.gif"
file_path = os.path.join(static_folder, "capybara.gif")

# 3. Ladda ner bilden
try:
    urllib.request.urlretrieve(image_url, file_path)
    print(f"✅ Bilden är sparad i: {file_path}")
    print("Starta om servern och titta på sidan!")
except Exception as e:
    print(f"❌ Något gick fel vid nedladdningen: {e}")