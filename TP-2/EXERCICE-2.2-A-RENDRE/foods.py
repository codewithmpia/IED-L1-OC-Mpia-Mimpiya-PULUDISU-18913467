import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fonction pour obtenir les produits alimentaires
def get_food_products(query, page_size=20):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&page_size={page_size}&json=1"
    response = requests.get(url)
    data = response.json()
    return data['products']

# Collecter les produits alimentaires
products = get_food_products("pizza")

# Extraire les informations pertinentes
product_data = []
for product in products:
    product_data.append({
        'product_name': product.get('product_name', 'N/A'),
        'brands': product.get('brands', 'N/A'),
        'energy_100g': product.get('nutriments', {}).get('energy_100g', 'N/A'),
        'sugars_100g': product.get('nutriments', {}).get('sugars_100g', 'N/A'),
        'fat_100g': product.get('nutriments', {}).get('fat_100g', 'N/A')
    })

# Convertir en DataFrame
df_products = pd.DataFrame(product_data)

# Afficher les premières lignes du DataFrame
print(df_products.head())

# Analyse des données
df_products['energy_100g'] = pd.to_numeric(df_products['energy_100g'], errors='coerce')
df_products['sugars_100g'] = pd.to_numeric(df_products['sugars_100g'], errors='coerce')
df_products['fat_100g'] = pd.to_numeric(df_products['fat_100g'], errors='coerce')

average_energy = df_products['energy_100g'].mean()
average_sugars = df_products['sugars_100g'].mean()
average_fat = df_products['fat_100g'].mean()

print(f"Calories moyennes par 100g : {average_energy} kJ")
print(f"Sucres moyens par 100g : {average_sugars} g")
print(f"Graisses moyennes par 100g : {average_fat} g")

# Visualisation des données
plt.figure(figsize=(10, 6))
plt.hist(df_products['energy_100g'].dropna(), bins=20, edgecolor='k')
plt.title('Distribution des calories par 100g')
plt.xlabel('Calories (kJ)')
plt.ylabel('Fréquence')
plt.show()