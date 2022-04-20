import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.by import By

import pandas as pd
import re
import random
import concurrent.futures

URLS = [
    "https://www.235grand.com/floorplans",
    "https://www.18park.com/floorplans",
    "https://www.225grandstreet.com/floorplans",
    "https://www.485marin.com/floorplans",
]


def clean_rent_price(some_rent_price):
    return re.sub(r"\n", " ", some_rent_price)


def get_property_name_from_url(url):
    return re.search(r"\.(\w+)", url).group(1)


def get_rentals(url):
    browser_driver = webdriver.Chrome()

    browser_driver.get(url)

    buttons = {
        '//button[text()="Studio"]': "Studio",
        '//button[text()="1 Bed"]': "1 BR",
        '//button[text()="2 Beds"]': "2 BR",
        '//button[text()="3 Beds"]': "3 BR",
    }

    rent_collection = {}
    df_collection = []

    for button, title in buttons.items():
        try:
            browser_driver.find_element(By.XPATH, button).click()
            time.sleep(1 + random.random())

            try:
                x_path_name = (
                    '//*[@id="collapse-tab0"]/div/div[1]/div[4]/div/div/span[2]'
                )

                rent_price = browser_driver.find_element(By.XPATH, x_path_name).text
            except:
                rent_price = pd.NA

            rent_collection["type_of_rental"] = title
            rent_collection["rent_price"] = [clean_rent_price(rent_price)]
            df = pd.DataFrame(data=rent_collection)
            df_collection.append(df)

        except:
            df_collection.append(pd.DataFrame())

    df = pd.concat(df_collection)
    df["url"] = url
    df["property_name"] = get_property_name_from_url(url)

    browser_driver.quit()

    return df


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        all_dfs = executor.map(get_rentals, URLS)

    df = pd.concat(all_dfs)
    df.reset_index(inplace=True, drop=True)
    df.to_csv("homes.csv")
