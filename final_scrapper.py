from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

driver = webdriver.Chrome()
driver.get("https://www.worldwildlife.org/places/amazon")
driver.maximize_window()

# accept cookie
cookie_accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
cookie_accept_btn.click()

data = []

# Section - 0: Scrape Titles
titles = []
title_menus = driver.find_elements(By.CSS_SELECTOR, "h2.hdr-primary")
for title in title_menus:
    titles.append(title.text)
data.append({"Titles": titles})

# Section - 1: Scrape FACTS
facts_main_div = driver.find_element(By.XPATH, "//div[@class='wysiwyg lead']")
elements_inside_facts = facts_main_div.find_elements(By.XPATH, ".//*")
facts_data = [el.text.strip() for el in elements_inside_facts if el.text.strip() != ""]
data.append({"Facts": facts_data})

# Section - 2: More Stories
wait = WebDriverWait(driver, 10)
more_stories_btn = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-unstyled"))
)
more_stories_btn.click()

story_links = driver.find_elements(By.CSS_SELECTOR, "ul.list-bordered-items li.row h2.h2 a")
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

driver.back()
data.append({"More Stories": more_stories_data})

# Section - 3: Scrape SPECIES Overview
species_main_div = driver.find_element(By.XPATH, "//div[@class='wysiwyg lead gutter-horiz-in']")
elements_inside_species = species_main_div.find_elements(By.XPATH, ".//*")
species_data = [el.text for el in elements_inside_species if el.text.strip() != ""]
data.append({"Species Overview": species_data})

# Section - 4: Scrape SPECIES in Depth
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
        time.sleep(1)

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

        # --- Why they matter ---
        try:
            main_matter_content = driver.find_element(
                By.XPATH, "//div[@class='description shaded-pop']/p"
            ).text.strip()
        except:
            main_matter_content = ""

        # --- Threats ---
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

        # --- WWF Work ---
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
                "Why They Matter": main_matter_content,
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

data.append({"Species Details": final_species_details})

# Section - 5: People & Community
try:
    people_community_main_div = driver.find_element(By.XPATH, "//div[@class='section-inner section-inner-padded section-inner-no-top-pad']")
    people_community_title = people_community_main_div.find_element(By.TAG_NAME, "span").text
    people_community_details = people_community_main_div.find_element(By.TAG_NAME, "p").text
    data.append({"People & Community": {"Title": people_community_title, "Details": people_community_details}})
except Exception as e:
    print("Error while extracting People & community:", e)

# Section - 6: Threats
try:
    threats_main_div = driver.find_element(By.XPATH, "//div[@class='section-inner section-inner-padded shaded-dark-pattern']")
    threats_title = threats_main_div.find_element(By.TAG_NAME, "span").text.strip()
    threats_text_divs = threats_main_div.find_elements(By.XPATH, ".//div[@class='row lead gutter-bottom-4']")
    threats_details = []
    for div in threats_text_divs:
        elements_inside_threats = div.find_elements(By.XPATH, ".//*")
        for el in elements_inside_threats:
            text = " ".join(el.text.split())
            if text and text not in threats_details:
                threats_details.append(text)
    data.append({"Threats": {"Title": threats_title, "Details": threats_details}})
except Exception as e:
    print("Error while extracting threats:", e)

# Section - 7: WWF Working
try:
    wwf_main_div = driver.find_element(By.XPATH, "//div[@class='section-inner section-inner-padded ']")
    wwf_title = wwf_main_div.find_element(By.TAG_NAME, "span").text.strip()
    wwf_text_divs = wwf_main_div.find_elements(By.XPATH, ".//div[@class='row lead gutter-bottom-4']")
    wwf_details = []
    for div in wwf_text_divs:
        elements_inside_wwf = div.find_elements(By.XPATH, ".//*")
        for el in elements_inside_wwf:
            text = " ".join(el.text.split())
            if text and text not in wwf_details:
                wwf_details.append(text)
    data.append({"WWF Working": {"Title": wwf_title, "Details": wwf_details}})
except Exception as e:
    print("Error while extracting Work of WWF:", e)

# Section - 8: Project
try:
    project_link = driver.find_element(By.XPATH, "//div[@class='gutter-bottom-4']/a")
    project_url = project_link.get_attribute("href")
    driver.get(project_url)
    project_heading = driver.find_element(By.TAG_NAME, "h1").text.strip()
    project_cards = driver.find_elements(By.CSS_SELECTOR, "div.span9.gutter-horiz-in")
    project_data = []
    for card in project_cards:
        try:
            card_title = card.find_element(By.TAG_NAME, "a").text.strip()
        except:
            card_title = ""
        try:
            card_text = card.find_element(By.TAG_NAME, "p").text.strip()
        except:
            card_text = ""
        project_data.append({"Project Title": card_title, "Project Description": card_text})
    data.append({"Project": {"Project Heading": project_heading, "Project Details": project_data}})
    driver.back()
except Exception as e:
    print("Error while extracting project section:", e)

# Section - 9: Publications
try:
    publication_links = driver.find_elements(By.XPATH, "//div[@class='gutter-bottom-4']/a")
    if len(publication_links) > 1:
        publication_links[1].click()
        time.sleep(1)
        publication_cards = driver.find_elements(By.XPATH, "//ul[contains(@class,'list-bordered-items') and contains(@class,'list-extra-spaced')]/li")
        publication_data = []
        for card in publication_cards:
            try:
                card_title = card.find_element(By.TAG_NAME, "h2").text.strip()
            except:
                card_title = ""
            try:
                card_description = card.find_element(By.TAG_NAME, "p").text.strip()
            except:
                card_description = ""
            publication_data.append({"Publication Title": card_title, "Publication Details": card_description})
        data.append({"Publications": publication_data})
        driver.back()
except Exception as e:
    print("Error while extracting Publication section:", e)

# Section - 10: Experts
expert_data = []
try:
    expert_ul_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//ul[contains(@class,'items') and contains(@class,'list-data')]"))
    )
    seen = set()
    while True:
        expert_cards = expert_ul_div.find_elements(By.XPATH, ".//a[contains(@class,'block') and contains(@class,'contain')]")
        for card in expert_cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, "strong.hdr").text.strip()
                details = card.find_element(By.CSS_SELECTOR, "em.details.base").text.strip()
                entry = (name, details)
                if entry not in seen:
                    seen.add(entry)
                    expert_data.append({"Expert Name": name, "Expert Details": details})
            except:
                continue
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "button.next, button.flickity-button.next, ul.nav a.next")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(1)
        except:
            break
except Exception as e:
    print("Expert section error:", e)
data.append({"Experts": expert_data})

# ---------- SAVE OUTPUT ----------
with open("amazon_all_sections.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("\n✅ All sections scraped successfully and saved to amazon_all_sections.json")
driver.quit()
