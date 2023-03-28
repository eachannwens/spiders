
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector

from webparse.steam_review_parse import steam_helper

driver = webdriver.Chrome()

# Crawl Target
driver.get('https://steamcommunity.com/app/990080/reviews/?browsefilter=toprated&snr=1_5_100010_')

# User Configuration
target_page = 10  # 100 pages contain about 1000 reviews
waiting_time = 1  # range of waiting in each time
tolerated_times = 30  # number of tolerant times for each page

# Start Crawling
page_counter = 1
current_tolerated = tolerated_times
while True:

    try:
        driver.implicitly_wait(waiting_time)
        driver.find_element(By.ID, 'page' + str(page_counter))
    except NoSuchElementException:
        # Not find
        # - rolling -> to avoid too much rolling - since one window maybe contain several page block
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        # - decrease tolerant
        if current_tolerated > 0:
            current_tolerated -= 1
            continue
        else:
            # Reach the end or Network break
            break
    else:
        # Find new page, reset tolerated counter
        if current_tolerated != tolerated_times:
            current_tolerated = tolerated_times
        # Page counter + 1
        page_counter += 1
        if page_counter == target_page:
            break

# Start Parsing
selector = Selector(text=driver.page_source)

steam_helper(selector, 'Hogwarts-Legacy.csv')

driver.quit()

