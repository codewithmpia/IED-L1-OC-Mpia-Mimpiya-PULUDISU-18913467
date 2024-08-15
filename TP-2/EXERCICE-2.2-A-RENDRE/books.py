import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fonction pour obtenir les livres de la catégorie "Science Fiction"
def get_books(query, max_results=40):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    response = requests.get(url)
    data = response.json()
    return data['items']

# Collecter les livres
books = get_books("subject:Science Fiction")

# Extraire les informations pertinentes
book_data = []
for book in books:
    volume_info = book['volumeInfo']
    book_data.append({
        'title': volume_info.get('title', 'N/A'),
        'authors': ', '.join(volume_info.get('authors', ['N/A'])),
        'publishedDate': volume_info.get('publishedDate', 'N/A'),
        'pageCount': volume_info.get('pageCount', 'N/A')
    })

# Convertir en DataFrame
df_books = pd.DataFrame(book_data)

# Afficher les premières lignes du DataFrame
print(df_books.head())

# Analyse des données
df_books['pageCount'] = pd.to_numeric(df_books['pageCount'], errors='coerce')
average_page_count = df_books['pageCount'].mean()
print(f"Longueur moyenne des livres : {average_page_count} pages")

# Visualisation des données
plt.figure(figsize=(10, 6))
plt.hist(df_books['pageCount'].dropna(), bins=20, edgecolor='k')
plt.title('Distribution des longueurs de livres')
plt.xlabel('Nombre de pages')
plt.ylabel('Fréquence')
plt.show()