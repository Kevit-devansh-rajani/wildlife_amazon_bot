# In this file, remaining sections are scrapped
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

data = []

# Section - 3: People & Community

try:
    people_community_main_div= driver.find_element(By.XPATH, "//div[@class='section-inner section-inner-padded section-inner-no-top-pad']")
    people_community_title = people_community_main_div.find_element(By.TAG_NAME, "span").text
    people_community_details = people_community_main_div.find_element(By.TAG_NAME, "p").text

    data.append({
        "Title" : people_community_title,
        "Details" : people_community_details
    })

except Exception as e:
    print("Error while extracting People & community:", e)

# Section - 4: Threats

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

    data.append({
        "Title": threats_title,
        "Details": threats_details
    })

except Exception as e:
    print("Error while extracting threats:", e)


# Section - 5: WWF Working
try:
    wwf_main_div = driver.find_element(By.XPATH, "//div[@class='section-inner section-inner-padded ']")
    wwf_title = threats_main_div.find_element(By.TAG_NAME, "span").text.strip()

    wwf_text_divs = wwf_main_div.find_elements(By.XPATH, ".//div[@class='row lead gutter-bottom-4']")

    wwf_details = []
    for div in wwf_text_divs:
        elements_inside_wwf = div.find_elements(By.XPATH, ".//*")
        for el in elements_inside_wwf:
            text = " ".join(el.text.split())
            if text and text not in wwf_details:
                wwf_details.append(text)

    data.append({
        "Title": wwf_title,
        "Details": wwf_details
    })

except Exception as e:
    print("Error while extracting Work of WWF:", e)

# Section - 6: Project

try:

    # Find and click the project link
    project_link = driver.find_element(By.XPATH, "//div[@class='gutter-bottom-4']/a")
    project_url = project_link.get_attribute("href")
    driver.get(project_url)

    # Main wrapper
    project_main_div = driver.find_element(By.CLASS_NAME, "wrapper")

    # Project heading
    project_heading = driver.find_element(By.TAG_NAME, "h1").text.strip()

    # Project names
    project_div_insider = driver.find_element(By.CSS_SELECTOR, "div.gutter-bottom-2")

    project_cards = project_div_insider.find_elements(By.CSS_SELECTOR, "div.span9.gutter-horiz-in")

    project_data = []

    for card in project_cards:
        card_title = card.find_element(By.TAG_NAME, "a").text.strip()
        card_text = card.find_element(By.TAG_NAME, "p").text.strip()

        project_data.append({
            "Project Title" : card_title,
            "Project Description" : card_text
        })

    data.append({
        "Project Heading": project_heading,
        "Project names & details" : project_data
    })

    driver.back()

except Exception as e:
    print("Error while extracting project section:", e)

# Section - 7: Publication Section

try:
    publication_divs = driver.find_elements(By.XPATH, "//div[@class='gutter-bottom-4']/a")
    publication_main_div = publication_divs[1]
    publication_main_div_btn = publication_main_div.get_attribute('href')
    driver.get(publication_main_div_btn)

    time.sleep(1)

    publication_cards = driver.find_elements(By.XPATH, "//ul[@class='list-bordered-items list-extra-spaced']")

    publication_data = []

    for card in publication_cards:
        card_title = card.find_element(By.TAG_NAME, "h2").text
        card_description = card.find_element(By.TAG_NAME, "p").text

        publication_data.append({
            "Publication Title" : card_title,
            "Publication Details" : card_description
        })

    data.append({
        "Publication Details" : publication_data 
    })

    driver.back()

except Exception as e:
    print("Error while extracting Publication section:", e)

# Section - 8: Experts Section

try:
    expert_data = []
    wait = WebDriverWait(driver, 10)
    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.nav a.next")))

    collected_names = set()
    previous_first_expert = None
    same_count = 0

    while len(collected_names) < 10 and same_count < 2:
        experts = driver.find_elements(By.CSS_SELECTOR, "ul.items.list-data a.block.contain")
        if experts:
            first_expert_name = experts[0].find_element(By.CSS_SELECTOR, "strong.hdr").text.strip()
            if first_expert_name == previous_first_expert:
                same_count += 1
            else:
                same_count = 0
            previous_first_expert = first_expert_name
            for expert in experts:
                name = expert.find_element(By.CSS_SELECTOR, "strong.hdr").text.strip()
                if name not in collected_names:
                    details = expert.find_element(By.CSS_SELECTOR, "em.details.base").text.strip()
                    expert_data.append({
                        "Expert Name": name,
                        "Expert Details": details
                    })
                    collected_names.add(name)
        next_button.click()
        time.sleep(0.5)

    data.append({
        "Expert Information": expert_data
    })
except Exception as e:
    print("Error while extracting Experts section:", e)

print(data)