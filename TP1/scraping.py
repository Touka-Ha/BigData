import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

def scrape_site(start_url, max_books=1000, delay=0.3):
    session = requests.Session()
    url = start_url
    books = []

    while url and len(books) < max_books:
        resp = session.get(url)
        if resp.status_code != 200:
            print("Failed to load:", resp.status_code)
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article", class_="product_pod")
        if not articles:
            print("No items found on this page, stopping.")
            break

        for article in articles:
            try:
                title = article.h3.a["title"]
                price = article.find("p", class_="price_color").get_text(strip=True)
                availability = article.find("p", class_="instock availability").get_text(strip=True)
            except Exception as e:
                print("Parse error, skipping one item:", e)
                continue

            books.append({
                "title": title,
                "price": price,
                "availability": availability
            })

            if len(books) >= max_books:
                break

        next_li = soup.find("li", class_="next")
        if next_li and next_li.a:
            next_href = next_li.a["href"]
            url = urljoin(url, next_href)
            time.sleep(delay)
        else:
            break

    return books

def main():
    start = "https://books.toscrape.com/catalogue/page-1.html"
    books = scrape_site(start_url=start, max_books=1000, delay=0.25)
    print(f"Total collected: {len(books)}")
    df = pd.DataFrame(books)
    df.to_csv("books_all.csv", index=False, encoding="utf-8-sig")
    print("Saved to books_all.csv")

if __name__ == "__main__":
    main()
