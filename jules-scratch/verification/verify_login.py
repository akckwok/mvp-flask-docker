from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Go to the login page
    page.goto("http://localhost:5000/")

    # Fill in the login form
    page.get_by_label("Username").fill("testuser")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()

    # Wait for the dashboard to load
    expect(page).to_have_url("http://localhost:5000/dashboard")
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

    # Take a screenshot of the dashboard
    page.screenshot(path="jules-scratch/verification/dashboard.png")

    # Logout
    page.get_by_role("link", name="Logout").click()

    # Wait for the login page to load again
    expect(page).to_have_url("http://localhost:5000/")
    expect(page.get_by_role("heading", name="Login")).to_be_visible()

    # Take a screenshot of the login page
    page.screenshot(path="jules-scratch/verification/login_after_logout.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
