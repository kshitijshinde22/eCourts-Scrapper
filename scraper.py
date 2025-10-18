import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class ECourtsScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
        os.makedirs("downloads", exist_ok=True)
        os.makedirs("results", exist_ok=True)

    # -----------------------------
    # Dropdown fetchers
    # -----------------------------
    def get_states(self):
        self.driver.get(self.base_url)
        select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "sess_state_code"))))
        return {o.text.strip(): o.get_attribute("value") for o in select.options[1:]}

    def get_districts(self, state_code):
        Select(self.driver.find_element(By.ID, "sess_state_code")).select_by_value(state_code)
        time.sleep(1)
        select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "sess_dist_code"))))
        return {o.text.strip(): o.get_attribute("value") for o in select.options[1:]}

    def get_complexes(self, state_code, district_code):
        Select(self.driver.find_element(By.ID, "sess_state_code")).select_by_value(state_code)
        Select(self.driver.find_element(By.ID, "sess_dist_code")).select_by_value(district_code)
        time.sleep(1)
        select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "court_complex_code"))))
        return {o.text.strip(): o.get_attribute("value") for o in select.options[1:]}

    def get_courts(self, complex_code):
        Select(self.driver.find_element(By.ID, "court_complex_code")).select_by_value(complex_code)
        time.sleep(1)
        select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "court_code"))))
        return {o.text.strip(): o.get_attribute("value") for o in select.options[1:]}

    # -----------------------------
    # Download cause list
    # -----------------------------
    def download_cause_list(self, state_code, district_code, complex_code, court_code, date_str):
        try:
            self.driver.get(self.base_url)
            Select(self.driver.find_element(By.ID, "sess_state_code")).select_by_value(state_code)
            Select(self.driver.find_element(By.ID, "sess_dist_code")).select_by_value(district_code)
            Select(self.driver.find_element(By.ID, "court_complex_code")).select_by_value(complex_code)
            Select(self.driver.find_element(By.ID, "court_code")).select_by_value(court_code)

            date_input = self.driver.find_element(By.ID, "causelist_date")
            date_input.clear()
            date_input.send_keys(date_str)

            self.driver.find_element(By.XPATH, "//button[text()='Go']").click()
            time.sleep(3)

            # PDF link if exists
            pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href,'.pdf')]")
            if pdf_links:
                pdf_url = pdf_links[0].get_attribute("href")
                file_name = f"downloads/cause_{court_code}_{date_str.replace('/','-')}.pdf"
                r = requests.get(pdf_url)
                with open(file_name, "wb") as f:
                    f.write(r.content)
                return {"success": True, "file": file_name}

            # else HTML table
            rows = self.driver.find_elements(By.XPATH, "//table//tr")
            data = []
            if len(rows) > 1:
                headers = [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]
                for row in rows[1:]:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    data.append({headers[i]: cols[i].text for i in range(len(cols))})
            json_file = f"results/cause_{court_code}_{date_str.replace('/','-')}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return {"success": True, "file": json_file}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_all_courts(self, state_code, district_code, complex_code, date_str):
        courts = self.get_courts(complex_code)
        results = []
        for name, code in courts.items():
            print(f"Downloading {name}...")
            res = self.download_cause_list(state_code, district_code, complex_code, code, date_str)
            results.append(res)
        return results

    def close(self):
        self.driver.quit()
