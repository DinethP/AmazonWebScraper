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

class GenerateReport:
  def __init__(self):
    pass

class AmazonAPI:
  def __init__(self, search_term, filters, base_url, currency):
    self.base_url = base_url
    self.search_term = search_term  # This is the NAME parameter that is passed when AmazonAPI() is called in main function
    options = get_web_driver_options() #Fetch the options
    set_ignore_certificate_error(options)
    set_browser_as_incognito(options)
    self.driver = get_chrome_web_driver(options)
    self.currency = currency
    self.price_filter = f"&rh=p_36%3A{filters['min']}00-{filters['max']}00"   # Filter the URL to set min/max price
    pass

  def run(self):
    print("Starting script...")
    print(f"Looking fir {self.search_term} prodcuts...")
    links = self.get_products_links()

    self.driver.quit()

  def get_products_links(self):
    self.driver.get(self.base_url)


if __name__ == '__main__':
  print("Hi")
  amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
  print(amazon.price_filter)
  amazon.run()