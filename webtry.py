
import numpy as np
import pandas as pd

import time
from selenium import webdriver
from scrapy.selector import Selector

games_list = {
    # 'Hogwarts Legacy': 'https://steamcommunity.com/app/990080/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Forza Horizon 5': 'https://steamcommunity.com/app/1551360/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Cities: Skylines': 'https://steamcommunity.com/app/255710/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Atomic Heart': 'https://steamcommunity.com/app/668580/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'It Takes Two': 'https://steamcommunity.com/app/1426210/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Sid Meier’s Civilization VI': 'https://steamcommunity.com/app/289070/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Red Dead Redemption 2': 'https://steamcommunity.com/app/1174180/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Grand Theft Auto V': 'https://steamcommunity.com/app/271590/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Overcooked! 2': 'https://steamcommunity.com/app/728880/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Monster Hunter: World': 'https://steamcommunity.com/app/582010/reviews/?browsefilter=toprated&snr=1_5_100010_',
    # 'Tomb Raider': 'https://steamcommunity.com/app/203160/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'Cyberpunk 2077': 'https://steamcommunity.com/app/1091500/reviews/?browsefilter=toprated&snr=1_5_100010_',
    'LEGO Star Wars: The Skywalker Saga': 'https://steamcommunity.com/app/920210/reviews/?browsefilter=toprated&snr=1_5_100010_'
}

for title in games_list:

    driver = webdriver.Chrome()
    driver.get(games_list[title])

    driver.implicitly_wait(1)

    single_trying_time = 5  # for normal trying
    keep_trying_count = 10  # retry times for one page
    keep_trying_time = 10   # retrying period

    counter = 0
    filename = title + '.csv'
    keep_trying_count_all = keep_trying_count

    # print(driver.get_window_size().get("width"), driver.get_window_size().get("height"))

    df = pd.DataFrame(columns=['author', 'home_url', 'helpful', 'funny', 'appraise', 'played_hour',
                               'post_month', 'post_day', 'games', 'reply', 'image', 'review'])

    while True:

        # Get the height of the page
        last_height = driver.execute_script("return document.body.scrollHeight")

        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load
        time.sleep(single_trying_time)

        # Get the new height of the page
        new_height = driver.execute_script("return document.body.scrollHeight")

        # print(last_height, '->', new_height)

        # Keep trying mechanism
        # If the height of the page has not changed, we have reached the bottom
        if new_height == last_height:
            if keep_trying_count > 0:
                time.sleep(keep_trying_time)
                keep_trying_count -= 1
                continue
            print(f'Arrive at bottom: {counter}')
            break
        else:
            if keep_trying_count != keep_trying_count_all:
                keep_trying_count = keep_trying_count_all
        counter += 1

    # Once we've generated all the dynamic content, we can use Scrapy's Selector to extract the data we need
    selector = Selector(text=driver.page_source)
    # Extract data here using Scrapy selectors
    app_cards = selector.xpath(
        '//div[contains(@class, "apphub_Card") and '
        'contains(@class, "modalContentLink") and '
        'contains(@class, "interactable")]'
    )  # Match at least one

    print(f'\nLog: number of reviews: {len(app_cards)}\n')

    card_index = 0
    for card in app_cards:
        # Helpful & Funny
        helpfulFunny = card.xpath('.//div[@class="found_helpful"]/text()').getall()
        if len(helpfulFunny) == 0:
            helpful = 0
            funny = 0
        elif len(helpfulFunny) == 1:
            helpful = helpfulFunny[0].strip().split(' ')[0]
            funny = 0
        else:
            helpful = helpfulFunny[0].strip().split(' ')[0]
            funny = helpfulFunny[1].strip().split(' ')[0]

        # Review
        appraise_text = card.xpath('.//div[@class="title"]/text()').get()
        appraise = 1 if appraise_text == 'Recommended' else 0
        played_hour = card.xpath('.//div[@class="hours"]/text()').get()
        if played_hour is not None:
            played_hour = played_hour.split(' ')[0]
        else:
            played_hour = 0

        # Date & Text
        date_info = card.xpath('.//div[@class="date_posted"]/text()').get().split(' ')
        date_month = date_info[1]
        date_day = date_info[2]
        review = card.xpath('.//div[@class="apphub_CardTextContent"]/text()').getall()
        review = ''.join(review).strip()

        # Own games
        games = card.xpath('.//div[contains(@class, "apphub_CardContentMoreLink") and contains(@class, "ellipsis")]/text()').get()
        if games is not None:
            games = games.split(' ')[0]
        else:
            games = 0

        # Reply
        reply = card.xpath('.//div[contains(@class, "apphub_CardCommentCount") and contains(@class, "alignNews")]/text()').get().strip()
        # Head image
        image = card.xpath('.//div[contains(@class, "appHubIconHolder")]/img').xpath('@src').extract_first()
        image = 1 if image != 'https://avatars.cloudflare.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb.jpg' else 0

        # Personal home link
        home_link = card.xpath('.//div[@class="apphub_friend_block_container"]/a').xpath('@href').extract_first()

        # Author
        author = card.xpath('.//div[contains(@class, "apphub_CardContentAuthorName")]/a/text()').get()

        # print(author)
        # print('helpful', helpful, 'funny', funny)
        # print(appraise_text, played_hour, 'hour(s)')
        # print('Posted in', date_month, date_day, '|', review)
        # print('I have', games, 'games')
        # print('This post has', reply, 'reply', 'user has', image, 'head image')
        # print(home_link)
        # print('-------------------------------------')

        # Load into Dataframe
        df = pd.concat([df, pd.DataFrame({
            'author': author,
            'home_url': home_link,
            'helpful': helpful,
            'funny': funny,
            'appraise': appraise,
            'played_hour': played_hour,
            'post_month': date_month,
            'post_day': date_day,
            'games': games,
            'reply': reply,
            'image': image,
            'review': review
        }, index=[0])], ignore_index=True)
        card_index += 1
        if card_index > 2000:
            break

    print(df)
    df.to_csv(filename, index=True)

    driver.quit()
