import json
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="pyszne", user="postgres", password="Dupadups123.", host="localhost", port="5432"
)
cursor = conn.cursor()

# Load the JSON
with open("pyszne_restaurants_details.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Insert each restaurant
for restaurant in data:
    cursor.execute("""
        INSERT INTO restaurants (
            name, url, rating, rating_count, cuisine_types, delivery_time,
            delivery_cost, min_order, header_image, avatar_image, colophon_info
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        restaurant['name'],
        restaurant['url'],
        restaurant['rating'],
        restaurant['rating_count'],
        json.dumps(restaurant['cuisine_types']),
        restaurant['delivery_time'],
        restaurant['delivery_cost'],
        restaurant['min_order'],
        restaurant['header_image'],
        restaurant['avatar_image'],
        restaurant['colophon_info']
    ))

conn.commit()
cursor.close()
conn.close()
