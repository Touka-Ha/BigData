import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_books_from_category(category_url):
    resp = requests.get(category_url)
    if resp.status_code != 200:
        print("Failed to load page:", resp.status_code)
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    
    books = []
    for article in soup.find_all("article", class_="product_pod"):
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").get_text().strip()
        availability = article.find("p", class_="instock availability").get_text().strip()
        books.append({
            "title": title,
            "price": price,
            "availability": availability
        })
    return books

def main():
    url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
    books = scrape_books_from_category(url)
    if not books:
        print("No data extracted.")
        return
    
    for b in books:
        print(b)
        
    df = pd.DataFrame(books)
    df.to_csv("books_travel.csv", index=False, encoding="utf-8-sig")
    print("✅ Data saved to books_travel.csv")

if __name__ == "__main__":
    main()