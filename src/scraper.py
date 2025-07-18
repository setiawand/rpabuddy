"""Simple RPA-based web scraper."""

import argparse
import json
import logging
import os
import shutil
import tempfile
from typing import List, Optional

from selenium.webdriver.support.ui import WebDriverWait, Select  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.common.exceptions import TimeoutException  # type: ignore

from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver  # type: ignore
from urllib.parse import urljoin
from selenium.webdriver.chrome.options import Options  # type: ignore


logger = logging.getLogger(__name__)


def _log_current_url(driver: webdriver.Chrome) -> None:
    """Log the current URL of the provided driver."""
    logger.info("Current page URL: %s", driver.current_url)

def _select_all_by_id(
    driver: webdriver.Chrome, element_id: str, exclude_values: Optional[List[str]] = None
) -> bool:
    """Select all options of a ``<select>`` element by ID.

    Returns ``True`` when the element exists. If the element can't be
    located, ``False`` is returned and a log message is emitted.
    """

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("id", element_id))
        )
        select_elem = Select(element)
    except Exception as exc:  # selenium.common.exceptions.NoSuchElementException
        logger.error("Element with id '%s' not found: %s", element_id, exc)
        return False

    excluded = set(exclude_values or [])

    selected_count = 0
    for option in select_elem.options:
        if option.get_attribute("value") in excluded:
            continue
        option.click()
        selected_count += 1

    logger.info("Selected %d options for %s", selected_count, element_id)
    return True


def scrape(url: str, selector: str) -> List[str]:
    """Open the web page and return texts matching CSS selector."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    with tempfile.TemporaryDirectory(prefix="selenium-") as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            _log_current_url(driver)
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
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    with tempfile.TemporaryDirectory(prefix="selenium-") as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        with webdriver.Chrome(options=options) as driver:
            logger.info("Opening URL %s", url)
            driver.get(url)
            _log_current_url(driver)

            logger.info("Clicking login link")
            driver.find_element("id", "login_link_top").click()
            _log_current_url(driver)

            logger.info("Entering username")
            driver.find_element("class name", username_selector).send_keys(username)
            logger.info("Entering password")
            driver.find_element("class name", password_selector).send_keys(password)
            logger.info("Submitting form")
            driver.find_element("id", submit_selector).click()
            _log_current_url(driver)

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
                _log_current_url(driver)
                return False

            if driver.find_elements("css selector", 'a[href="index.cgi?logout=1"]'):
                _log_current_url(driver)
                logger.info("Login successful")
                return True

            logger.info("Login failed: invalid credentials")
            _log_current_url(driver)
            return False


def login_and_advanced_search(
    url: str,
    username: str,
    password: str,
    username_selector: str,
    password_selector: str,
    submit_selector: str,
    csv_output: Optional[str] = None,
    download_dir: str = ".",
) -> bool:
    """Login and perform an advanced search on contoh.com.

    If ``csv_output`` is provided, the search result will be saved to the
    specified file in CSV format. When ``csv_output`` is not specified, the
    result will be saved as ``download.csv`` inside ``download_dir``.
    """

    logger.info("Starting login and search flow for %s", url)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

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
                _log_current_url(driver)
                return False

            if not driver.find_elements(
                "css selector", 'a[href="index.cgi?logout=1"]'
            ):
                logger.info("Login failed: invalid credentials")
                _log_current_url(driver)
                return False

            logger.info("Login successful, navigating to search page")
            driver.find_element("link text", "Search").click()
            _log_current_url(driver)
            WebDriverWait(driver, 10).until(EC.url_contains("query.cgi"))

            logger.info("Switching to advanced search")
            driver.get(urljoin(url, "query.cgi?format=advanced"))
            _log_current_url(driver)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        ("css selector", "#tab_advanced.selected")
                    )
                )
            except TimeoutException:
                logger.error("Advanced search page did not load")
                return False

            logger.info("Selecting product Company")
            if not _select_all_by_id(driver, "product"):
                return False

            logger.info("Selecting all components")
            if not _select_all_by_id(driver, "component"):
                return False

            logger.info("Selecting all bug statuses except CLOSED")
            if not _select_all_by_id(driver, "bug_status", ["CLOSED"]):
                return False

            logger.info("Selecting all resolutions")
            if not _select_all_by_id(driver, "resolution"):
                return False

            logger.info("Submitting search")
            driver.find_element("id", "Search").click()
            _log_current_url(driver)

            logger.info("Waiting for search results")
            try:
                csv_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(("link text", "CSV"))
                )
            except TimeoutException:
                logger.error("CSV link not found on results page")
                return False

            if not csv_output:
                csv_output = os.path.join(download_dir, "download.csv")
                logger.info("csv-output not provided; using default %s", csv_output)

            logger.info("Downloading CSV to %s", csv_output)
            csv_url = csv_link.get_attribute("href")
            logger.info("csv_url %s", csv_url)
            driver.get(csv_url)
            _log_current_url(driver)
            try:
                pre = driver.find_element("tag name", "pre")
                logger.info("<pre> tag found in CSV download")
                csv_text = pre.text
            except Exception:
                logger.info("No <pre> tag found; using page source")
                csv_text = driver.page_source
            logger.info("csv_output %s", csv_output)
            os.makedirs(os.path.dirname(csv_output) or ".", exist_ok=True)
            with open(csv_output, "w", encoding="utf-8") as f:
                f.write(csv_text)

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
    parser.add_argument(
        "--csv-output",
        help="Save advanced search result CSV to this file",
    )
    parser.add_argument(
        "--download-dir",
        default=".",
        help="Directory to save CSV when --csv-output is not provided",
    )

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
            args.csv_output,
            args.download_dir,
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
