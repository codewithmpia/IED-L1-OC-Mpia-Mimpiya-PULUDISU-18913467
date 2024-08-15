from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import re

# Configuration de Selenium
chrome_options = Options()
# Exécuter en mode sans entête
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Spécifiez le chemin vers ChromeDriver
service = ChromeService(ChromeDriverManager().install())

# Initialiser le WebDriver avec les options et le service
driver = webdriver.Chrome(service=service, options=chrome_options)

# Liste des URL
urls = [
    "https://www.wikipedia.org",
    "https://www.w3schools.com",
    "https://developer.mozilla.org/fr",
    "https://www.python.org",
    "https://flask.palletsprojects.com/en/3.0.x",
    "https://www.djangoproject.com",
    "https://vuejs.org",
    "https://tailwindcss.com",
    "https://getbootstrap.com",
    "https://www.fun-mooc.fr/fr",
    "https://grafikart.fr",
]

# Dossier pour enregistrer les captures d'écran
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

for url in urls:
    try:
        driver.get(url)
        # Attendre que le contenu de la page soit complètement chargé
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        title = driver.title
        title_cleaned = re.sub(r'[\/:*?"<>|]', '', title)
        # Remplacer les espaces par des underscores
        title_cleaned = title_cleaned.replace(' ', '_')
        if not title_cleaned:
            title_cleaned = "screenshot"
        filename = f"screenshots/{title_cleaned}.png"

        driver.save_screenshot(filename)
        print(f"Capture d'écran sauvegardée pour {url} sous {filename}")
    except Exception as e:
        print(f"Erreur lors de la capture d'écran pour {url}: {e}")

driver.quit()
