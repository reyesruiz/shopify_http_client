'''
HTTPS client to connect to shopify:
Copyright 2023 Reyes Ruiz
'''

from pathlib import Path
import sys
import time
import json
import requests
from com_digitalruiz_my_logger import my_logger

LOGGER = my_logger.set_logger(module_name=sys.argv[0], loglevel='INFO')

def __get_shopify_configs():
    '''
    Getting configs from ~/.Shopify-Config.json
    '''
    home = str(Path.home())
    file_name = home + '/.Shopify-Config.json'
    with open(file_name, "r", encoding='utf-8') as json_file:
        shopify_config = json.load(json_file)
    return shopify_config

def __get_shopify_token():
    '''
    Getting shopify api access token.
    '''
    shopify_config = __get_shopify_configs()
    shopify_access_token = shopify_config['shopify_access_token']
    return shopify_access_token

def get(url):
    '''
    Simple http get method to grab data from shopify api links
    '''
    LOGGER.info("Getting %s", url)
    shopify_access_token = __get_shopify_token()
    headers = {'X-Shopify-Access-Token': shopify_access_token, \
        'Content-Type': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=60)
    except requests.exceptions.RequestException as error:
        LOGGER.error("Unable to get data to %s, will sleep for 1 minute and try again", url)
        LOGGER.error(error)
        return get(url)
    if response.status_code == 200:
        contents = []
        contents.append(response.content)
        if 'Link' in response.headers:
            for link in response.headers['Link'].split(','):
                if 'next' in link.split(';')[1]:
                    url = link.split(';')[0].strip().replace('<','').replace('>','')
                    contents = contents + get(url)
        return contents
    if response.status_code == 429:
        LOGGER.error("Too many requests, sleeping... for 2 minutes")
        LOGGER.error(response.headers)
        time.sleep(120)
        return get(url)
    LOGGER.error("Unable to get %s", url)
    LOGGER.error(response)
    return False

def put(url, data):
    '''
    Simple http put method to upload data to shopify
    '''
    LOGGER.info("Putting to %s", url)
    shopify_access_token = __get_shopify_token()
    headers = {'X-Shopify-Access-Token': shopify_access_token, \
        'Content-Type': 'application/json'}
    try:
        response = requests.put(url, headers=headers, json=data, timeout=60)
    except requests.exceptions.RequestException as error:
        LOGGER.error("Unable to put data to %s, will sleep for 1 minute and try again", url)
        LOGGER.error(error)
        time.sleep(60)
        return put(url, data)
    if response.status_code in (200, 201):
        content = response.text
        return content
    if response.status_code == 429:
        LOGGER.error("Too many requests, sleeping... for 2 minutes")
        LOGGER.error(response.headers)
        time.sleep(120)
        return put(url, data)
    LOGGER.error("Unable to put data to %s", url)
    LOGGER.error(response)
    return False


def post(url, data):
    '''
    Simple http post method to upload data to shopify
    '''
    LOGGER.info("Posting to %s", url)
    shopify_access_token = __get_shopify_token()
    headers = {'X-Shopify-Access-Token': shopify_access_token, \
        'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
    except requests.exceptions.RequestException as error:
        LOGGER.error("Unable to post data to %s, will sleep for 1 minute and try again", url)
        LOGGER.error(error)
        time.sleep(60)
        return post(url, data)
    if response.status_code in (200, 201):
        content = response.text
        return content
    if response.status_code == 429:
        LOGGER.error("Too many requests, sleeping... for 2 minutes")
        LOGGER.error(response.headers)
        time.sleep(120)
        return post(url, data)
    LOGGER.error("Unable to post data to %s, will sleep for 1 minute and try again", url)
    LOGGER.error(response)
    return False

def set_shopify_admin_url():
    '''
    Building shopify admin api url using store url plus api version,
    '''
    shopify_config = __get_shopify_configs()
    shopify_store_name = shopify_config['shopify_store_name']
    shopify_admin_api_version = shopify_config['shopify_admin_api_version']
    shopify_url = "https://" + shopify_store_name + ".myshopify.com"
    shopify_admin_api_url =  '/'.join([shopify_url,
            'admin',
            'api',
            shopify_admin_api_version])
    return shopify_admin_api_url

def __get_paginated_url(response):
    for link in response.headers['Link'].split(','):
        if 'next' in link.split(';')[1]:
            url = link.split(';')[0].strip().replace('<','').replace('>','')
            response = get(url)
            if response:
                return response
    return False
