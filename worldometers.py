# The idea: to bring a list of all countries and their links (233 countries) and then go inside each country, 
#and extract the population timeline (from one year to another)
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm

BASE_URL = "https://www.worldometers.info"
MAIN_URL = f"{BASE_URL}/world-population/population-by-country/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def get_country_links():
    resp = requests.get(MAIN_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.find("table")
    links = []
    if not table:
        raise RuntimeError("I did not find the countries table on the home page.")
    for tr in table.find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2:
            a = tds[1].find("a")
            if a and "href" in a.attrs:
                country_name = a.get_text(strip=True)
                country_link = BASE_URL + a["href"]
                links.append((country_name, country_link))
    return links

def find_best_table_on_page(html_text):
    try:
        dfs = pd.read_html(html_text)
    except Exception:
        return None

    if not dfs:
        return None

    for df in dfs:
        cols_lower = [str(c).lower() for c in df.columns.astype(str)]
        if any('year' in c for c in cols_lower):
            return df
    for df in dfs:
        if df.shape[1] >= 1:
            first_col = df.iloc[:,0].astype(str).str.extract(r'(\d{3,4})', expand=False).dropna()
            if not first_col.empty:
                years = pd.to_numeric(first_col, errors='coerce').dropna()
                if ((years >= 1800) & (years <= 2050)).sum() >= max(3, len(years)//4):
                    return df

    return dfs[0]

def scrape_country_population(country_name, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        df = find_best_table_on_page(html)
        if df is None or df.empty:
            print(f"There is no valid table in {country_name}")
            return []

        df = df.fillna("").astype(str)

        rows = []
        for _, row in df.iterrows():
            row_vals = [str(v).strip() for v in row.tolist()]
            if all(v == "" for v in row_vals):
                continue
            rows.append([country_name] + row_vals)
        cols = [str(c).strip() for c in df.columns.tolist()]
        return cols, rows

    except Exception as e:
        print(f"Error while processing {country_name}: {e}")
        return None

def main(output_csv="worldometers_population_all_countries_robust.csv", delay=0.6):
    all_rows = []
    all_columns_candidates = []

    links = get_country_links()
    print(f"Number of countries: {len(links)}")

    for name, link in tqdm(links, desc="Countries"):
        result = scrape_country_population(name, link)
        if result is None:
            time.sleep(delay)
            continue
        cols_rows = result
        if cols_rows is None:
            time.sleep(delay)
            continue

        cols, rows = cols_rows
        if rows:
            all_rows.extend(rows)
            all_columns_candidates.append(cols)
        time.sleep(delay)

    if not all_rows:
        print("No rows collected.")
        return
        
    longest_cols = max(all_columns_candidates, key=lambda c: len(c))

    final_columns = ["Country"] + longest_cols

    normalized_rows = []
    for r in all_rows:
        needed = len(final_columns) - len(r)
        if needed > 0:
            r_extended = r + [""] * needed
        else:
            r_extended = r[:len(final_columns)]
        normalized_rows.append(r_extended)

    df = pd.DataFrame(normalized_rows, columns=final_columns)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ {len(df)} row saved in {output_csv}")

if __name__ == "__main__":
    main()
