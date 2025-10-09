from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

PATH = "/home/kevit/Documents/chromedriver"
service = Service(PATH)
driver = webdriver.Chrome(service=service)

driver.get("https://www.worldwildlife.org/places/amazon")
driver.maximize_window()

# accept cookie
cookie_accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
cookie_accept_btn.click()

# Section - 0: Scrape Titles

titles = []
title_menus = driver.find_elements(By.CSS_SELECTOR, "h2.hdr-primary")
for title in title_menus:
    titles.append(title.text)
print(f"Titles : {titles}")

# Section - 1: Scrape FACTS

facts_main_div = driver.find_element(By.XPATH, "//div[@class='wysiwyg lead']")
elements_inside_facts = facts_main_div.find_elements(By.XPATH, ".//*")

facts_data = [el.text.strip() for el in elements_inside_facts if el.text.strip() != ""]
print(facts_data)

# ---------- More Stories ----------

wait = WebDriverWait(driver, 10)

more_stories_btn = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-unstyled"))
)
more_stories_btn.click()

story_links = driver.find_elements(By.CSS_SELECTOR, "ul.list-bordered-items li.row h2.h2 a")
print(f"Total articles : {len(story_links)}")

more_stories_data = []

for i in range(len(story_links)):
    story_links = driver.find_elements(By.CSS_SELECTOR, "ul.list-bordered-items li.row h2.h2 a")
    link = story_links[i]
    title = link.text.strip()

    parent_li = link.find_element(By.XPATH, "./ancestor::li")

    try:
        paragraph_element = parent_li.find_element(By.CSS_SELECTOR, "div.wysiwyg.lead p")
        paragraph = paragraph_element.text.strip()
    except:
        try:
            paragraph_element = parent_li.find_element(By.CSS_SELECTOR, "div.wysiwyg.lead")
            paragraph = paragraph_element.text.strip()
        except:
            paragraph = ""

    more_stories_data.append({
        "Title": title,
        "Paragraph": paragraph
    })

    print(f"Scraped: {title}")

driver.back()

# Section - 2: Scrape SPECIES

species_main_div = driver.find_element(By.XPATH, "//div[@class='wysiwyg lead gutter-horiz-in']")
elements_inside_species = species_main_div.find_elements(By.XPATH, ".//*")

species_data = [el.text for el in elements_inside_species if el.text.strip() != ""]
print(species_data)

# ---------- Species Details ----------

final_species_details = []
species_items_count = len(driver.find_elements(By.CSS_SELECTOR, "ul.items li.item-circle"))

for i in range(species_items_count):
    try:
        species_items = driver.find_elements(By.CSS_SELECTOR, "ul.items li.item-circle")
        specie = species_items[i]

        name = specie.find_element(By.CLASS_NAME, "name").text.strip().upper()
        print(f"Scraping species: {name}")

        link_element = specie.find_element(By.TAG_NAME, "a")
        link_element.click()
        time.sleep(2)

        sub_titles_div = driver.find_elements(By.CSS_SELECTOR, "h2.hdr-primary span")
        sub_titles = [t.text.strip() for t in sub_titles_div]

        # --- Fact content (clean + deduped) ---
        try:
            main_fact_content = driver.find_element(
                By.XPATH, "//div[@class='gutter-top-in-4 gutter-bottom-in-2 gutter-horiz-in']"
            )
            elements_inside_facts = main_fact_content.find_elements(By.XPATH, ".//p | .//li | .//span")
            facts = [el.text.strip() for el in elements_inside_facts if el.text.strip() != ""]

            clean_facts = []
            for f in facts:
                cleaned = " ".join(f.split())
                if cleaned not in clean_facts:
                    clean_facts.append(cleaned)

            fact_content = clean_facts

        except:
            fact_content = []

        # --- Why there matter content ---
        try:
            main_matter_content = driver.find_element(
                By.XPATH, "//div[@class='description shaded-pop']/p"
            ).text.strip()
        except:
            main_matter_content = ""

        # --- Threat content ---
        try:
            main_threat_content = driver.find_element(
                By.XPATH, "//div[@class='row lead gutter-bottom-4']"
            )
            threat_elements = main_threat_content.find_elements(By.XPATH, ".//p | .//li")
            threats = []
            for t in threat_elements:
                text = " ".join(t.text.split())
                if text and text not in threats:
                    threats.append(text)
        except:
            threats = []

        # --- WWF Work content ---
        try:
            main_wwf_content = driver.find_element(
                By.XPATH, "//div[@class='lead wysiwyg gutter-horiz-in gutter-top-3 gutter-bottom-3']"
            )
            wwf_elements = main_wwf_content.find_elements(By.XPATH, ".//p | .//li")
            wwf_texts = []
            for w in wwf_elements:
                text = " ".join(w.text.split())
                if text and text not in wwf_texts:
                    wwf_texts.append(text)
        except:
            wwf_texts = []

        species_info = {
            "Species Name": name,
            "Details": [{
                "Titles": sub_titles,
                "Fact": fact_content,
                "Why There Matter": main_matter_content,
                "Threat": threats,
                "WWF Work": wwf_texts
            }]
        }

        final_species_details.append(species_info)
        driver.back()
        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        continue

# ---------- SAVE OUTPUT ----------

output_json = "species_details.json"
output_text = "species_details.txt"

# Save JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(final_species_details, f, indent=4, ensure_ascii=False)

# Save as readable text
with open(output_text, "w", encoding="utf-8") as f:
    for sp in final_species_details:
        f.write(f"=== {sp['Species Name']} ===\n")
        for d in sp["Details"]:
            f.write("\n".join([f"Titles: {', '.join(d['Titles'])}"]))
            f.write("\n\n--- FACTS ---\n")
            for fact in d["Fact"]:
                f.write(f"- {fact}\n")
            f.write("\n--- WHY THEY MATTER ---\n")
            f.write(f"{d['Why There Matter']}\n")
            f.write("\n--- THREATS ---\n")
            for t in d["Threat"]:
                f.write(f"- {t}\n")
            f.write("\n--- WWF WORK ---\n")
            for w in d["WWF Work"]:
                f.write(f"- {w}\n")
            f.write("\n\n" + "="*60 + "\n\n")

print(f"\n✅ Data saved to:\n- {output_json}\n- {output_text}")
driver.quit()
