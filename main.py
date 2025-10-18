import bs4
import requests
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_image(url, folder_name, num):
    # write image to file
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder_name, str(num) + ".jpg"), 'wb') as file:
            file.write(response.content)

# create a directory to save images
folder_name = 'images'
if not os.path.isdir(folder_name):
    os.makedirs(folder_name)

# read driver path from config.json
with open("example_config.json") as f:
    config = json.load(f)

service = Service(executable_path=config["driver_path"])
driver = webdriver.Chrome(service=service)

num_images = int(input("How many images to download: "))
search_input = input("Images to download (e.g. cats, cars): ")
search_URL = f"https://www.google.com/search?q={search_input}&source=lnms&tbm=isch"
driver.get(search_URL)

# handle cookie pop-up
try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.='Reject all' or .='Odrzuć wszystko']"))
    ).click()
except:
    pass

driver.execute_script("window.scrollTo(0, 0);")

page_html = driver.page_source
pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')
containers = pageSoup.findAll('div', {
    'class': "eA0Zlc WghbWd FnEtTd mkpRId m3LIae RLdvSe qyKxnc ivg-i PZPZlf GMCzAd"
})

len_containers = len(containers)
print("Container count:", len_containers)

for i in range(1, len_containers + 1):
    if i > num_images:
        break
    if i % 25 == 0:  # skip related searches
        continue

    container_path = f'//*[@id="rso"]/div/div/div[1]/div/div/div[{i}]'

    try:
        driver.find_element(By.XPATH, container_path).click()
        time.sleep(3)

        # get the HTML after the panel opens
        page_html = driver.page_source
        pageSoup = bs4.BeautifulSoup(page_html, "html.parser")

        img_tags = pageSoup.find_all("img", {"class": "sFlh5c FyHeAf iPVvYb"})

        # the one with visible tag is the full res image
        visible_img = None
        for img in img_tags:
            style = img.get("style", "")
            if "visibility: hidden" not in style:
                visible_img = img
                break

        if visible_img:
            imageURL = visible_img.get("src")
            print(f"{i}: Full res URL ->", imageURL)
        
        # download the image
            try:
                download_image(imageURL, folder_name, i)
                print(f"Downloaded {i}/{len_containers}: {imageURL}")
            except:
                print(f"Couldn't download image {i}, skipping...")
    
        else:
            print(f"{i}: No visible full res image found.")

    except Exception as e:
        print(f"Error at index {i}: {e}")

driver.quit()





