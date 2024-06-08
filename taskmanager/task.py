from celery import shared_task
from .coin_scraper import CoinMarketCapScraper
import redis
import json
from redis.commands.json.path import Path

@shared_task
def scrape_coin_data(acronym):
    scraper = CoinMarketCapScraper(acronym)
    data = scraper.scrape()
    return data
