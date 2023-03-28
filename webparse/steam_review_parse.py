
import os
import pandas as pd
from scrapy.selector import Selector


def steam_helper(selector: Selector, filename):

    df = pd.DataFrame(columns=['author', 'home_url', 'helpful', 'funny', 'appraise', 'played_hour',
                               'post_month', 'post_day', 'games', 'reply', 'image', 'review'])

    app_cards = selector.xpath(
        '//div[contains(@class, "apphub_Card") and '
        'contains(@class, "modalContentLink") and '
        'contains(@class, "interactable")]'
    )  # Match at least one

    print(f'\nLog: number of reviews: {len(app_cards)}\n')

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

        # Review appraise
        appraise_text = card.xpath('.//div[@class="title"]/text()').get()
        appraise = 1 if appraise_text == 'Recommended' else 0

        # Played hour
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

        # Number of owned games
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

    # Finished
    print(df)

    # Save to disk
    df.to_csv(os.path.join('../csvoutput', filename), index=True)
    print('Save to', os.path.join('../csvoutput', filename))


