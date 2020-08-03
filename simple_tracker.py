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
import time

class GenerateReport:
  def __init__(self):
    pass

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

    self.driver.quit()

  def get_products_info(self, links):
    # ASIN - Amazon Standard Identification Number
    # asins is a list of all asins of searched items
    asins = self.get_asins(links)
    products = []
    for asin in asins:
      product = self.get_single_product_info(asin)

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
    return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]  

  def get_products_links(self):
     # Open up the amazon website homepage using webdriver
    self.driver.get(self.base_url)
    element = self.driver.find_element_by_id("twotabsearchtextbox")
    element.send_keys(self.search_term)
    element.send_keys(Keys.ENTER)
    # Wait to load page
    time.sleep(2) 
    # Concatenate price filter string to search item url(the url
    # when we searched the search term)
    self.driver.get(f"{self.driver.current_url}{self.price_filter}")
     # Wait to load page
    time.sleep(2)

    # HTML parent element containing search results
    result_list = self.driver.find_elements_by_class_name('s-result-list') 
    links = []
    try:
        #results will loop through each search item and get each of their links into an array
        results = result_list[0].find_elements_by_xpath(  
            "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
        # Loop through the links in results and filter out the elements with href attribute (actual links)
        links = [link.get_attribute('href') for link in results] 
         # links is an array of all the links
        return links
    # exception for when there are no links                                              
    except Exception as e:      
        print("Didn't get any products...")
        print(e)
        return links


if __name__ == '__main__':
  print("Hi")
  amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
  print(amazon.price_filter)
  amazon.run()