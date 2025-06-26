"""Simple RPA-based web scraper."""

import argparse
import json
import logging
import shutil
import tempfile
from typing import List

from selenium.webdriver.support.ui import WebDriverWait, Select  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.common.exceptions import TimeoutException  # type: ignore

from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore


logger = logging.getLogger(__name__)


def _select_all_by_id(driver: webdriver.Chrome, element_id: str) -> bool:
    """Select all options of a ``<select>`` element by ID.

    Returns ``True`` when the element exists. If the element can't be
    located, ``False`` is returned and a log message is emitted.
    """

    try:
        select_elem = Select(driver.find_element("id", element_id))
    except Exception as exc:  # selenium.common.exceptions.NoSuchElementException
        logger.error("Element with id '%s' not found: %s", element_id, exc)
        return False

    for option in select_elem.options:
        option.click()

    logger.info("Selected %d options for %s", len(select_elem.options), element_id)
    return True


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

    logger.info("Starting login flow for %s", url)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    with tempfile.TemporaryDirectory(prefix="selenium-") as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        with webdriver.Chrome(options=options) as driver:
            logger.info("Opening URL %s", url)
            driver.get(url)

            logger.info("Clicking login link")
            driver.find_element("id", "login_link_top").click()

            logger.info("Entering username")
            driver.find_element("class name", username_selector).send_keys(username)
            logger.info("Entering password")
            driver.find_element("class name", password_selector).send_keys(password)
            logger.info("Submitting form")
            driver.find_element("id", submit_selector).click()

            logger.info("Checking login result")
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(
                        "css selector", 'a[href="index.cgi?logout=1"]'
                    )
                    or d.find_elements("id", "error_msg")
                )
            except TimeoutException:
                logger.info(
                    "Login failed: no logout link or error message detected"
                )
                return False

            if driver.find_elements("css selector", 'a[href="index.cgi?logout=1"]'):
                logger.info("Login successful")
                return True

            logger.info("Login failed: invalid credentials")
            return False


def login_and_advanced_search(
    url: str,
    username: str,
    password: str,
    username_selector: str,
    password_selector: str,
    submit_selector: str,
) -> bool:
    """Login and perform an advanced search on contoh.com."""

    logger.info("Starting login and search flow for %s", url)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    with tempfile.TemporaryDirectory(prefix="selenium-") as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        with webdriver.Chrome(options=options) as driver:
            logger.info("Opening URL %s", url)
            driver.get(url)

            logger.info("Clicking login link")
            driver.find_element("id", "login_link_top").click()

            logger.info("Entering username")
            driver.find_element("class name", username_selector).send_keys(username)
            logger.info("Entering password")
            driver.find_element("class name", password_selector).send_keys(password)
            logger.info("Submitting form")
            driver.find_element("id", submit_selector).click()

            logger.info("Checking login result")
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(
                        "css selector", 'a[href="index.cgi?logout=1"]'
                    )
                    or d.find_elements("id", "error_msg")
                )
            except TimeoutException:
                logger.info(
                    "Login failed: no logout link or error message detected"
                )
                return False

            if not driver.find_elements(
                "css selector", 'a[href="index.cgi?logout=1"]'
            ):
                logger.info("Login failed: invalid credentials")
                return False

            logger.info("Login successful, navigating to search page")
            driver.find_element("link text", "Search").click()
            WebDriverWait(driver, 10).until(EC.url_contains("query.cgi"))

            logger.info("Switching to advanced search")
            driver.get("https://contoh.com/query.cgi?format=specific")

            logger.info("Selecting product Company")
            if not _select_all_by_id(driver, "product"):
                return False

            logger.info("Selecting all components")
            if not _select_all_by_id(driver, "component"):
                return False

            logger.info("Selecting all bug statuses")
            if not _select_all_by_id(driver, "bug_status"):
                return False

            logger.info("Selecting all resolutions")
            if not _select_all_by_id(driver, "resolution"):
                return False

            logger.info("Submitting search")
            driver.find_element("id", "Search").click()

            return True


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="RPA web scraper")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--selector", help="CSS selector to extract")

    parser.add_argument("--login", action="store_true", help="Run login flow")
    parser.add_argument(
        "--advanced-search",
        action="store_true",
        help="Run login flow and perform advanced search",
    )
    parser.add_argument("--username", help="Username for login")
    parser.add_argument("--password", help="Password for login")
    parser.add_argument(
        "--config",
        help="Path to JSON config file containing username and password",
    )
    parser.add_argument("--username-selector", help="Class for username field")
    parser.add_argument("--password-selector", help="Class for password field")
    parser.add_argument("--submit-selector", help="ID for submit button")

    args = parser.parse_args()

    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except FileNotFoundError:
            parser.error(f"Config file {args.config} not found")

        args.username = args.username or cfg.get("username")
        args.password = args.password or cfg.get("password")

    if args.advanced_search:
        required = [
            args.username,
            args.password,
            args.username_selector,
            args.password_selector,
            args.submit_selector,
        ]
        if not all(required):
            parser.error(
                "advanced-search requires username, password, and element selectors"
            )

        success = login_and_advanced_search(
            args.url,
            args.username,
            args.password,
            args.username_selector,
            args.password_selector,
            args.submit_selector,
        )
        print("Pencarian selesai" if success else "Pencarian gagal")
        return

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
