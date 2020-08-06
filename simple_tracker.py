from amazon_config import(
  get_web_driver_options,
  get_chrome_web_driver,
  set_ignore_certificate_error,
  set_browser_as_incognito,
  NAME,
  CURRENCY,
  FILTERS,
  BASE_URL,
  DIRECTORY
)
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import json
from datetime import datetime
import time


class GenerateReport:
  def __init__(self, file_name, filters, base_link, currency, data):
    self.data = data
    self.file_name = file_name
    self.filters = filters
    self.base_link = base_link
    self.currency = currency
    report = {
      'title': self.file_name,
      'date': self.get_now(),
      'best_item': self.get_best_item(),
      'currency': self.currency,
      'filters': self.filters,
      'base_link': self.base_link,
      'products': self.data
    }
    print("Creating report...")
    with open(f'{DIRECTORY}/{file_name}.json', 'w') as f:
      json.dump(report, f)
    print("Done...")

  def get_now(self):
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

  def get_best_item(self):
    try:
      return sorted(self.data, key=lambda k: k['price'])[0]
    except Exception as e:
      print(e)
      print("Problem with sorting items")
      return None


class AmazonAPI:
  def __init__(self, search_term, filters, base_url, currency):
    self.base_url = base_url
    # This is the NAME parameter that is passed when AmazonAPI() is called in main function
    self.search_term = search_term
    #Fetch the options  
    options = get_web_driver_options() 
    set_ignore_certificate_error(options)
    set_browser_as_incognito(options)
    # Call the webdriver with the added flags (options)
    self.driver = get_chrome_web_driver(options) 
    self.currency = currency
    # Add price min and max to amazon url
    self.price_filter = f"&rh=p_36%3A{filters['min']}00-{filters['max']}00"   
    pass

  # This is the MAIN function
  def run(self):
    print("Starting script...")
    print(f"Looking for {self.search_term} prodcuts...")
    links = self.get_products_links()
    time.sleep(1)
    if not links:
      print("Stopped script")
      return
    print(f"Got {len(links)} links to products!")
    print("Getting info about products")
    products = self.get_products_info(links)
    print(f"Fetched info about {len(products)} products...")
    self.driver.quit()
    return products

  def get_products_links(self):
     # Open up the amazon website homepage using webdriver
    self.driver.get(self.base_url)
    # Search for item
    element = self.driver.find_element_by_id("twotabsearchtextbox")
    element.send_keys(self.search_term)
    element.send_keys(Keys.ENTER)
    # Wait to load page
    time.sleep(2) 
    # Concatenate price filter string to search results URl(the url
    # that gives the search results)
    self.driver.get(f"{self.driver.current_url}{self.price_filter}")
     # Wait to load page
    time.sleep(2)

    # HTML parent element containing search results
    result_list = self.driver.find_elements_by_class_name('s-result-list')
    links = []
    try:
        #results is an array of all items in the first search page. Each array element will have all the HTML elements of each item
        results = result_list[0].find_elements_by_xpath(  
            "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
        # Loop through the HTML elements of that item and get the product link (actual link to the item)
        links = [link.get_attribute('href') for link in results] 
         # links is an array of all the links for each search item
        return links
    # exception for when there are no links                                              
    except Exception as e:      
        print("Didn't get any products...")
        print(e)
        return links

  def get_products_info(self, links):
    # ASIN - Amazon Standard Identification Number
    # asins is a list of all asins of searched items
    asins = self.get_asins(links)
    products = []
    for asin in asins: # Can splice this asins array to limit how many items we want to fetch
      product = self.get_single_product_info(asin)
      if product:
        products.append(product)
    return products

  # Get info for each searched products
  def get_single_product_info(self, asin):
    print(f"Product ID: {asin} - fetching data...")
    product_short_url = self.shorten_url(asin)
    # The param is needed to change language
    self.driver.get(f"{product_short_url}?language=en_GB")
    time.sleep(2)

    title = self.get_title()
    seller = self.get_seller()
    price = self.get_price()

    # Check if all 3 items were fetched for the product
    if title and seller and price:
      product_info = {
        'asin': asin,
        'url': product_short_url,
        'title': title,
        'seller': seller,
        'price': price
      }
      return product_info
    return None

  def get_title(self):
    try:
      # Fetch the title text of the item
      return self.driver.find_element_by_id('productTitle').text
    except Exception as e:
      print(e)
      print(f"Can't get title of a product - {self.driver.current_url}")
      return None

  def get_seller(self):
    try:
      return self.driver.find_element_by_id('bylineInfo').text
    except Exception as e:
      print(e)
      print(f"Can't get seller of a product - {self.driver.current_url}")
      return None

  def get_price(self):
    price = None
    try:
      price = self.driver.find_element_by_id('priceblock_ourprice').text
      price = self.convert_price(price)
    except NoSuchElementException:
      try:
          availability = self.driver.find_element_by_id('availability').text
          # Check if string 'Available' is in the element text
          if 'Available' in availability:
              price = self.driver.find_element_by_class_name('olp-padding-right').text
              price = price[price.find(self.currency):]
              price = self.convert_price(price)
      except Exception as e:
          print(e)
          print(f"Can't get price of a product - {self.driver.current_url}")
          return None
    except Exception as e:
        print(e)
        print(f"Can't get price of a product - {self.driver.current_url}")
        return None
    return price

    # Convert the price string to a float
  def convert_price(self, price):
    price = price.split(self.currency)[1]
    try:
        price = price.split("\n")[0] + "." + price.split("\n")[1]
    except:
        Exception()
    try:
        price = price.split(",")[0] + price.split(",")[1]
    except:
        Exception()
    return float(price)
  
  # Remove all unnecessary attributes/product names/keywords from the long URL
  # This makes sure that our code works even if product names are changed (the ASIN never changes) 
  def shorten_url(self, asin):
    return self.base_url + 'dp/' + asin

  # Get all ASIN's of all search items
  def get_asins(self, links):
    return [self.get_asin(link) for link in links]

  # Get ASIN for each product from its link
  def get_asin(self, product_link):
    # Splice the link to get the unique product ID (it is inbetween '.../dp/' and '/ref...')
    # We +4 to start index to account for '/dp/'
    return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]  


if __name__ == '__main__':
  amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
  data =  amazon.run()
  GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)