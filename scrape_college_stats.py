from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

POSITION_TO_DATA_HTML_ID = """
QB passing_standard
WR receiving_standard
RB rushing_standard
te receiving_standard
de defense_standard
t defense_standard
lb defense_standard
db defense_standard
dt defense_standard
g defense_standard
cb defense_standard
nt defense_standard
c defense_standard
s defense_standard
olb defense_standard
ilb defense_standard
dl defense_standard
"""

def scrape_csv_with_selenium(url):
    options = Options()

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options
    )

    driver.get(url)
    try: 
        wait = WebDriverWait(driver, 10)
        # Wait for page to load, find "Share and Export" dropdown menu
        menu_li = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#receiving_standard_sh > div:nth-child(4) > ul > li.hasmore")
        ))
        # Scroll to the "Share and Export" dropdown menu and hover over it
        driver.execute_script("arguments[0].scrollIntoView(true);", menu_li)
        driver.execute_script("arguments[0].classList.add('drophover');", menu_li)
        time.sleep(0.5)
        # Click the "Get table as CSV" button
        csv_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#receiving_standard_sh > div:nth-child(4) > ul:nth-child(1) > li:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(3) > button:nth-child(1)')
        ))
        csv_btn.click()
        # Get the CSV data element
        pre = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '#csv_receiving_standard')
        ))
        return pre.text
    except Exception as e:
        # add some sort of logging here
        driver.quit()

urls = [
    "https://www.sports-reference.com/cfb/players/marvin-harrison-jr-1.html?__hstc=223721476.3706d1f9b94a335726d4ba0d479fe0bb.1737576656753.1744734659770.1744846699642.11&__hssc=223721476.1.1744846699642&__hsfp=2335339835",
]

for u in urls:
    csv_data = scrape_csv_with_selenium(u)
    print(f"--- CSV for {u} ---\n{csv_data}\n")
