import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import JpmorganchaseItem
from itemloaders.processors import TakeFirst
base = 'https://www.jpmorganchase.com/services/json/dynamic-feed.service/parent=jpmc/jpmorganchase/us/en/home/news-stories/stories/communities&comp=content-parsys/dynamic_grid_copy_co&partition=p{}.json'


class JpmorganchaseSpider(scrapy.Spider):
	name = 'jpmorganchase'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for post in data['items']:
			url = post['href']
			try:
				date = post['item_date']
			except:
				date = None
			title = post['title']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		self.page += 1
		yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="event__body__text"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=JpmorganchaseItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
