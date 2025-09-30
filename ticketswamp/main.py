from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get("https://www.ticketswap.nl/event/stella-lowenzahnhonig/c6a4e19e-f0de-44ab-a451-9ebb8c61aa0b")

# Solve CAPTCHA manually
input("Solve the CAPTCHA and press Enter...")

# Get cookies after solving
cookies = driver.get_cookies()
print(cookies)

# Now you can use these cookies in subsequent requests
