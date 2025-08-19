from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Go to login page
    page.goto("http://localhost:5173/login.html")

    # Wait for the page to load
    expect(page.get_by_role("heading", name="Login")).to_be_visible()

    # Take a screenshot
    page.screenshot(path="jules-scratch/verification/login-page.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
