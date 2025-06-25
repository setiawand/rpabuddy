"""Simple RPA-based web scraper."""

import argparse
import shutil
import tempfile
from typing import List

from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.common.exceptions import TimeoutException  # type: ignore

from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore


def scrape(url: str, selector: str) -> List[str]:
    """Open the web page and return texts matching CSS selector."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    with tempfile.TemporaryDirectory(prefix="selenium-") as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)
    return [el.get_text(strip=True) for el in elements]


def login(
    url: str,
    username: str,
    password: str,
    username_selector: str,
    password_selector: str,
    submit_selector: str,
) -> bool:
    """Automate a login page and return True if navigation occurs."""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    with tempfile.TemporaryDirectory(prefix="selenium-") as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)

            driver.find_element("id", "login_link_top").click()
            
            driver.find_element("class name", username_selector).send_keys(
                username
            )
            driver.find_element("class name", password_selector).send_keys(
                password
            )
            driver.find_element("id", submit_selector).click()

            try:
                WebDriverWait(driver, 10).until(EC.url_changes(url))
            except TimeoutException:
                return False

            return True


def main() -> None:
    parser = argparse.ArgumentParser(description="RPA web scraper")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--selector", help="CSS selector to extract")

    parser.add_argument("--login", action="store_true", help="Run login flow")
    parser.add_argument("--username", help="Username for login")
    parser.add_argument("--password", help="Password for login")
    parser.add_argument("--username-selector", help="Class for username field")
    parser.add_argument("--password-selector", help="Class for password field")
    parser.add_argument("--submit-selector", help="ID for submit button")

    args = parser.parse_args()

    if args.login:
        required = [
            args.username,
            args.password,
            args.username_selector,
            args.password_selector,
            args.submit_selector,
        ]
        if not all(required):
            parser.error("login requires username, password, and element selectors")

        success = login(
            args.url,
            args.username,
            args.password,
            args.username_selector,
            args.password_selector,
            args.submit_selector,
        )
        print("Login berhasil" if success else "Login gagal")
        return

    if not args.selector:
        parser.error("--selector is required unless --login is specified")

    results = scrape(args.url, args.selector)
    for text in results:
        print(text)


if __name__ == "__main__":
    main()
