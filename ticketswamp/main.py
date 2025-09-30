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

# Solve CAPTCHA manually
input("Solve the CAPTCHA and press Enter...")

# Try to accept cookies automatically
try:
    # Wait a moment for the page to load
    import time
    time.sleep(2)
    
    # Common cookie acceptance button selectors
    cookie_selectors = [
        "button[id*='accept']",
        "button[class*='accept']", 
        "button[id*='cookie']",
        "button[class*='cookie']",
        "button[id*='consent']",
        "button[class*='consent']",
        "button:contains('Accept')",
        "button:contains('Accept All')",
        "button:contains('I Accept')",
        "button:contains('Agree')",
        "button:contains('OK')",
        "[data-testid*='accept']",
        "[data-testid*='cookie']",
        ".cookie-accept",
        ".accept-cookies",
        "#accept-cookies",
        "#cookie-accept"
    ]
    
    cookie_accepted = False
    for selector in cookie_selectors:
        try:
            if selector.startswith("button:contains("):
                # Handle text-based selectors differently
                text = selector.split("'")[1]
                elements = driver.find_elements("xpath", f"//button[contains(text(), '{text}')]")
            else:
                elements = driver.find_elements("css selector", selector)
            
            if elements:
                element = elements[0]
                if element.is_displayed() and element.is_enabled():
                    print(f"Found cookie button with selector: {selector}")
                    element.click()
                    print("✅ Cookies accepted automatically!")
                    cookie_accepted = True
                    time.sleep(1)  # Wait for page to update
                    break
        except Exception as e:
            continue
    
    if not cookie_accepted:
        print("⚠️ No cookie acceptance button found automatically")
        
except Exception as e:
    print(f"⚠️ Error trying to accept cookies: {e}")

# Print the page content after solving CAPTCHA
print("\n=== PAGE CONTENT AFTER CAPTCHA ===")
print(driver.page_source)
print("=== END OF POST-CAPTCHA CONTENT ===\n")

# Monitor availableTicketsCount in a loop every second
import re
import time
import subprocess
from datetime import datetime

def get_ticket_count():
    """Extract availableTicketsCount from the page"""
    try:
        # Method 1: Search for the JSON pattern in page source
        page_source = driver.page_source
        pattern = r'"availableTicketsCount":(\d+)'
        match = re.search(pattern, page_source)
        
        if match:
            return int(match.group(1)), "HTML"
        
        # Method 2: Try to find it in JavaScript variables
        js_result = driver.execute_script("""
            // Look for availableTicketsCount in various places
            if (window.availableTicketsCount !== undefined) {
                return window.availableTicketsCount;
            }
            if (window.ticketData && window.ticketData.availableTicketsCount !== undefined) {
                return window.ticketData.availableTicketsCount;
            }
            if (window.eventData && window.eventData.availableTicketsCount !== undefined) {
                return window.eventData.availableTicketsCount;
            }
            return null;
        """)
        
        if js_result is not None:
            return int(js_result), "JavaScript"
            
        return None, None
        
    except Exception as e:
        return None, f"Error: {e}"

print("\n🔄 Starting ticket count monitoring...")
print("Press Ctrl+C to stop monitoring")
print("=" * 50)

try:
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        tickets_count, source = get_ticket_count()
        
        if tickets_count is not None:
            if tickets_count > 0:
                print(f"🚨 [{current_time}] 🎫 TICKETS AVAILABLE: {tickets_count} (from {source})")
            else:
                print(f"[{current_time}] 🎫 Available Tickets: {tickets_count} (from {source})")
        else:
            print(f"[{current_time}] ⚠️ Could not find ticket count ({source})")
        
        time.sleep(0.5)  # Wait 0.5 seconds before next check
        
except KeyboardInterrupt:
    print("\n\n🛑 Monitoring stopped by user")
except Exception as e:
    print(f"\n❌ Error during monitoring: {e}")

# Get cookies after solving
cookies = driver.get_cookies()
print("=== COOKIES AFTER CAPTCHA ===")
print(cookies)
print("=== END OF COOKIES ===")

# Now you can use these cookies in subsequent requests
