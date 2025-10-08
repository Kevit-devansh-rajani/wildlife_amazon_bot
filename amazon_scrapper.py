from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
print(titles)


# Section - 1: Scrape FACTS

facts_main_div = driver.find_element(By.XPATH, "//div[@class='wysiwyg lead']")
elements_inside_facts = facts_main_div.find_elements(By.XPATH, ".//*")

facts_data = [el.text for el in elements_inside_facts if el.text.strip() != ""]
print(facts_data)

# ---------- More Stories ----------

wait = WebDriverWait(driver, 10)

more_stories_btn = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-unstyled"))
) 
more_stories_btn.click()

story_links = driver.find_elements(By.CSS_SELECTOR, "ul.list-bordered-items li.row h2.h2 a")
print(f"Totlal articles : {len(story_links)}")

data = []

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

    data.append({
        "Title": title,
        "Paragraph": paragraph
    })

    print(f"Scraped: {title}")

driver.back()

# Section - 2: Scrape SPECIES

species_main_div = driver.find_element(By.XPATH, "//div[@class='wysiwyg lead gutter-horiz-in']")
elements_inside_species = species_main_div.find_elements(By.XPATH, ".//*")

species_data = [el.text for el in elements_inside_species if el.text.strip() != ""]

# ---------- Species Details ----------

species_items = driver.find_elements(By.CSS_SELECTOR, "ul.items li.item-circle")
species_names = []
species_titles = []

for specie in species_items:
    name = specie.find_element(By.CLASS_NAME, "name").text
    species_names.append(name)
    

for specie in species_items:
    try:        
        link_element = specie.find_element(By.TAG_NAME, "a")
        link_element.click()
        
        main_titles = driver.find_elements(By.CSS_SELECTOR, "h2.hdr-primary span")
        titles = [t.text for t in main_titles]
        species_titles.append(titles)

        driver.back()
        time.sleep(1)
        
    except Exception as e:
        print("Error:", e)

for name, title in zip(species_names,species_titles):
    print({
        "Name" : name,
        "Titles" : title
    })
