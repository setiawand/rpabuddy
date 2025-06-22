"""Simple RPA-based web scraper."""

import argparse
import shutil
import tempfile
from typing import List

from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore


def scrape(url: str, selector: str) -> List[str]:
    """Open the web page and return texts matching CSS selector."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    user_data_dir = tempfile.mkdtemp(prefix="selenium-")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)

    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)
    return [el.get_text(strip=True) for el in elements]


def main() -> None:
    parser = argparse.ArgumentParser(description="RPA web scraper")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--selector", required=True, help="CSS selector to extract")
    args = parser.parse_args()

    results = scrape(args.url, args.selector)
    for text in results:
        print(text)


if __name__ == "__main__":
    main()
