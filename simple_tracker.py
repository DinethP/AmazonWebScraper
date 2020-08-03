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
    time.sleep(3)
    self.driver.quit()

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