import logging
import re
from w3lib.url import canonicalize_url, url_query_cleaner

from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import ProductItem, ProductItemLoader


logger = logging.getLogger(__name__)


def load_product(response):
    """Load a ProductItem from the product page response."""
    loader = ProductItemLoader(item=ProductItem(), response=response)

    url = url_query_cleaner(response.url, ['snr'], remove=True)
    url = canonicalize_url(url)
    loader.add_value('url', url)

    found_id = re.findall('/app/(.*?)/', response.url)
    if found_id:
        id = found_id[0]
        reviews_url = f'http://steamcommunity.com/app/{id}/reviews/?browsefilter=mostrecent&p=1'
        loader.add_value('reviews_url', reviews_url)
        loader.add_value('id', id)


    # Publication details.
    loader.add_css('app_name', '.apphub_AppName ::text')
    loader.add_css('specs', '.game_area_details_specs a ::text')
    loader.add_css('tags', 'a.app_tag::text')

    genre = loader.add_xpath('genre','(//div[@class="details_block"])[1]/a/text()')
    loader.add_value('genre', genre)
    if not genre:
        genre= ['Unknown']

    image_url=loader.add_xpath('image_url','//*[@id="game_highlights"]/div[1]/div/div[1]/img/@src')

    description = loader.add_css('description', '.game_description_snippet ::text')
    loader.add_value('description', description)
    if not description:
        description = ['None']
        loader.add_value('description', description)

    # finds price, checks for discount, if not available returns None
    discount_price=['None']
    price = response.css('.game_purchase_price ::text').extract_first()
    if not price:
        price = response.css('.discount_original_price ::text').extract_first()
        loader.add_css('discount_price', '.discount_final_price ::text')
    loader.add_value('discount_price', discount_price)
    loader.add_value('price', price)
    if not price:
        price=['None']
    loader.add_value('price', price)

    genre_test = loader.add_xpath('genre_test','(//div[@class="details_block"])[1]/a/text()')
    loader.add_value('genre_test', genre_test)
    if not genre_test:
        genre_test=['Unknown']
        loader.add_value('genre_test', genre_test)


    sentiment = response.css('.game_review_summary').xpath('../*[@itemprop="description"]/text()').extract()
    loader.add_value('sentiment', sentiment)
    if not sentiment:
        sentiment = ['None']
    loader.add_value('sentiment', sentiment)

    loader.add_css('n_reviews', '.responsive_hidden', re='\(([\d,]+) reviews\)')

    metascore = loader.add_xpath(
        'metascore',
        '//div[@id="game_area_metascore"]/div[contains(@class, "score")]/text()')
    if not metascore:
        metascore = [0]
    loader.add_value('metascore', metascore)

    positive = loader.add_xpath('positive' ,'//div[@id="reviews_filter_options"]/div[1]/div[2]/div/label[2]/span/text()')
    if not positive:
        positive = [0]
    loader.add_value('positive', positive)
    negative = loader.add_xpath('negative' ,'//div[@id="reviews_filter_options"]/div[1]/div[2]/div/label[3]/span/text()')
    if not negative:
        negative = [0]
    loader.add_value('negative', negative)


    developer = loader.add_xpath('developer','//div[@id="developers_list"]/a/text()' )
    if not developer:
        developer=['Unknown']
        loader.add_value('developer', developer)

    publisher =loader.add_xpath('publisher','//div[@id="game_highlights"]/div[1]/div/div[3]/div/div[4]/div[2]/a/text()')
    if not publisher:
        publisher=['Unknown']
        loader.add_value('publisher', publisher)

    #checks if the field release_date exists, if it doesn't adds value by default
    release_date = loader.add_css('release_date','.date::text')
    if not release_date:
        release_date = ['2020-10-02']
    loader.add_value('release_date', release_date)

    release_date_string = loader.add_css('release_date_string','.date::text')
    if not release_date_string:
        release_date_string = ['Not available']
    loader.add_value('release_date_string', release_date_string)

    early_access = response.css('.early_access_header')
    if early_access:
        loader.add_value('early_access', True)
    else:
        loader.add_value('early_access', False)

    return loader.load_item()


class ProductSpider(CrawlSpider):
    name = 'products'
    start_urls = ['http://store.steampowered.com/search/?sort_by=Released_DESC']

    allowed_domains = ['steampowered.com']

    rules = [
        Rule(LinkExtractor(
             allow='/app/(.+)/',
             restrict_css='#search_result_container'),
             callback='parse_product'),
        Rule(LinkExtractor(
             allow='page=(\d+)',
             restrict_css='.search_pagination_right'))
    ]

    def __init__(self, steam_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_id = steam_id

    def start_requests(self):
        if self.steam_id:
            yield Request(f'http://store.steampowered.com/app/{self.steam_id}/',
                          cookies ={'mature_content': '1'},
                          callback=self.parse_product)
        else:
            yield from super().start_requests()

    def parse_product(self, response):
        # Circumvent age selection form.
        if '/agecheck/app' in response.url:
            form = response.css('#agegate_box form')
            action = form.xpath('@action').extract_first()
            name = form.xpath('input/@name').extract_first()
            value = form.xpath('input/@value').extract_first()

            formdata = {
                name: value,
                'ageDay': '1',
                'ageMonth': 'January',
                'ageYear': '1955'
            }

            yield FormRequest(
                url=action,
                method='POST',
                formdata=formdata,
                callback=self.parse_product
            )

        else:
            yield load_product(response)




