import bookies.bluebet
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    bookies.bluebet.main(browser)
    browser.close()