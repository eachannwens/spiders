
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, JavascriptException, WebDriverException
from scrapy.selector import Selector

from webparse.steam_review_parse import steam_helper

# User Configuration
infinity_search = 0
target_page = 100  # 100 pages contain about 1000 reviews
waiting_time = 5  # minute(s)

games_dict = {
    'Hogwarts Legacy': 'https://steamcommunity.com/app/990080/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Forza Horizon 5': 'https://steamcommunity.com/app/1551360/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Cities: Skylines': 'https://steamcommunity.com/app/255710/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Atomic Heart': 'https://steamcommunity.com/app/668580/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'It Takes Two': 'https://steamcommunity.com/app/1426210/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Sid Meier’s Civilization VI': 'https://steamcommunity.com/app/289070/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Red Dead Redemption 2': 'https://steamcommunity.com/app/1174180/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Grand Theft Auto V': 'https://steamcommunity.com/app/271590/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Overcooked! 2': 'https://steamcommunity.com/app/728880/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Monster Hunter: World': 'https://steamcommunity.com/app/582010/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Tomb Raider': 'https://steamcommunity.com/app/203160/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Cyberpunk 2077': 'https://steamcommunity.com/app/1091500/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'LEGO Star Wars: The Skywalker Saga': 'https://steamcommunity.com/app/920210/reviews/?browsefilter=toprated&snr=1_5_100010_'
}

for games_title in games_dict:

    # Initialize
    driver = webdriver.Chrome()
    # Crawl Target
    driver.get(games_dict[games_title])

    # Start Crawling
    wait = 0.1
    tolerated_times = 60 * waiting_time / wait  # number of tolerant times for each page
    page_counter = 1
    current_tolerated = tolerated_times
    while True:

        try:
            curr_id = 'page' + str(page_counter)
            time.sleep(wait)

            # Find see more content
            try:
                see_more_click = driver.find_element(By.XPATH, '//div[@id="GetMoreContentBtn"]')
            except NoSuchElementException:
                pass
            except WebDriverException:
                print('WebDriverException')
                break
            else:
                try:
                    if see_more_click.is_displayed():
                        more_click = driver.find_element(By.XPATH, '//div[@id="GetMoreContentBtn"]/a')
                        try:
                            ActionChains(driver).click(more_click).perform()
                            print('Click for more content', 'Page:', page_counter)
                        except ElementNotInteractableException:
                            pass
                except JavascriptException:
                    print('JavascriptException')
                    break

            driver.find_element(By.ID, curr_id)
            # print(curr_id)
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
                print('Reach the end or Network break')
                break
        else:
            # Find new page, reset tolerated counter
            if current_tolerated != tolerated_times:
                current_tolerated = tolerated_times
            # Page counter + 1
            page_counter += 1
            if page_counter % 10 == 0:
                time.sleep(3)
            if (page_counter == target_page) & (infinity_search == 0):
                print('Finish searching.')
                break

    # Start Parsing
    selector = Selector(text=driver.page_source)

    steam_helper(selector, '-'.join(games_title.split(' ')) + '.csv', page_counter)

    driver.quit()

