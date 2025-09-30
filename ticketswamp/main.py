from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# Use the new ChromeDriver we downloaded
chromedriver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chromedriver-mac-arm64', 'chromedriver')
service = Service(chromedriver_path)

# Configure Chrome options to appear as a regular user browser
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

# Add additional stealth preferences
prefs = {
    "profile.default_content_setting_values": {
        "notifications": 2,
        "geolocation": 2,
        "media_stream": 2,
    },
    "profile.default_content_settings.popups": 0,
    "profile.managed_default_content_settings.images": 2
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=service, options=chrome_options)

# Execute script to remove webdriver property and other automation traces
driver.execute_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    window.chrome = {runtime: {}};
    Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
""")
driver.get("https://www.ticketswap.nl/event/stella-lowenzahnhonig/c6a4e19e-f0de-44ab-a451-9ebb8c61aa0b")

# Print the HTML content of the page
print("=== PAGE HTML CONTENT ===")
print(driver.page_source)
print("=== END OF HTML CONTENT ===")

# Solve CAPTCHA manually
input("Solve the CAPTCHA and press Enter...")

# Get cookies after solving
cookies = driver.get_cookies()
print(cookies)

# Now you can use these cookies in subsequent requests
