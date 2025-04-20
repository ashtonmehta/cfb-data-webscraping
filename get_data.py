#!/usr/bin/env python3
import sys
import time
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ─── adjust these paths/names as needed ─────────────────────────────────────
INPUT_CSV = "./data/receiving_standard.csv"     # your CSV with Player,Pos,College Stats URL
# ─────────────────────────────────────────────────────────────────────────────

# mapping from Pos to the table HTML ID
POSITION_TO_DATA_HTML_ID = {
    "QB": "passing_standard",
    "WR": "receiving_standard",
    "TE": "receiving_standard",
    "RB": "rushing_standard",
}

def clean_csv_text(raw: str) -> str:
    """
    Strip off the SR attribution header so we begin at 'Season,Team,...'
    """
    for i, line in enumerate(raw.splitlines()):
        if line.startswith("Season,"):
            return "\n".join(raw.splitlines()[i:])
    raise ValueError("Could not find CSV header in:\n" + raw[:200])

def scrape_csv_with_selenium(url: str, html_id: str) -> str | None:
    """Return raw CSV text from <pre id="csv_{html_id}">, or None on failure."""
    options = Options()
    options.add_argument("--headless")  # run in headless mode
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    try:
        driver.set_page_load_timeout(30)
        driver.get(url)
        wait = WebDriverWait(driver, 5)

        # 0) ensure the share-wrapper exists
        wrappers = driver.find_elements(By.CSS_SELECTOR, f"#{html_id}_sh")
        if not wrappers:
            print(f"[!] No section #{html_id}_sh found on page.")
            return None
        wrapper = wrappers[0]

        # 1) un-collapse if there’s a togglebutton
        toggles = wrapper.find_elements(By.CSS_SELECTOR, "button.togglebutton")
        if toggles:
            toggles[0].click()

        # 2) reveal the “Share & Export” dropdown
        menu_li = wrapper.find_element(By.CSS_SELECTOR, "li.hasmore")
        driver.execute_script("arguments[0].classList.add('drophover')", menu_li)
        time.sleep(0.2)

        # 3) click the CSV button
        csv_btn = menu_li.find_element(
            By.CSS_SELECTOR, "button.tooltip[tip*='comma-separated values']"
        )
        try:
            csv_btn.click()
        except WebDriverException:
            # fallback if an overlay intercepts the click
            driver.execute_script("arguments[0].click();", csv_btn)

        # 4) grab the <pre> text
        pre = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f"#csv_{html_id}")
        ))
        return pre.text

    except TimeoutException:
        print("[!] Timeout while scraping", url)
        return None

    finally:
        driver.quit()

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <row_index>")
        sys.exit(1)

    idx = int(sys.argv[1])
    df_in = pd.read_csv(INPUT_CSV)
    if idx < 0 or idx >= len(df_in):
        print(f"[!] Index {idx} out of range (0–{len(df_in)-1})")
        sys.exit(1)

    row = df_in.iloc[idx]
    player = row["Player"]
    pos    = row["Pos"]
    url    = row["College Stats URL"]

    html_id = POSITION_TO_DATA_HTML_ID.get(pos)
    if not html_id:
        print(f"[!] No table mapping for position '{pos}', aborting.")
        sys.exit(1)

    print(f"Scraping index={idx}: {player} ({pos}) → {url}")
    raw_csv = scrape_csv_with_selenium(url, html_id)
    if not raw_csv:
        print("[!] Failed to retrieve CSV.")
        sys.exit(1)

    # clean & parse
    clean = clean_csv_text(raw_csv)
    df_out = pd.read_csv(StringIO(clean))
    df_out["Player"] = player
    df_out["Pos"]    = pos

    # show it
    print(df_out)

    # optional: save to file
    out_file = f"./receiving/player_{idx}_{player.replace(' ', '_')}.csv"
    df_out.to_csv(out_file, index=False)
    print(f"✅ Saved to {out_file}")

if __name__ == "__main__":
    main()
