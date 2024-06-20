import bookies.bluebet as test_script
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    test_script.main(browser)
    browser.close()