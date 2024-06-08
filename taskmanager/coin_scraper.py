from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import re

class CoinMarketCapScraper:
    def __init__(self, coin_acronym):
        self.coin_acronym = coin_acronym
        self.url = f"https://coinmarketcap.com/currencies/{coin_acronym.lower()}/"
        self.data = {
            'output':{}
        }

    def fetch_page(self):
        driver_path = './taskmanager/chrome/chromedriver.exe'
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.get(self.url)

    def parse_data(self):

        def extract_single_item_by_class_name(class_name):
            value = self.driver.find_element(By.CLASS_NAME, class_name).text
            return value

        def extract_multi_item_by_class_name(class_name):
            value = self.driver.find_elements(By.CLASS_NAME, class_name)
            list = [element.text for index, element in enumerate(value)]
            return list

        def extract_multi_items_by_class_name(class_name):
            value = self.driver.find_elements(By.CLASS_NAME, class_name)
            return value

        def remove_char_before_dollor(item):
            if '$' in item:
                return item[item.find('$'):]
            return item

        def convert_to_numeric_values(item):
            # Find all sequences of digits, possibly separated by commas or dots
            numeric_strings = re.findall(r'[\d,.]+', item)
            # Join the found sequences and remove any commas
            numeric_value = ''.join(numeric_strings).replace(',', '')
            # Convert to appropriate numeric type
            if '.' in numeric_value:
                return float(numeric_value)
            elif numeric_value.isdigit():
                return int(numeric_value)
            return ''

        def lists_to_dict(keys, values):
            return dict(zip(keys, values))

        # class_name_coin = 'bEFegK'
        xpath = '//span[@data-role="coin-name"]'
        try:
            self.data['coin'] = str(self.driver.find_element(By.XPATH, xpath).text)
        except:
            self.data['coin'] = ''

        class_name_price = 'fsQm'
        try:
            price = extract_single_item_by_class_name(class_name_price)
            self.data['output']['price'] = float(price.replace('$', '').replace(',',''))
        except:
            self.data['output']['price'] = ''

        class_name_price_change = 'bgxfSG'
        try:
            price_change = extract_single_item_by_class_name(class_name_price_change)
            percent_index = price_change.find('%')
            self.data['output']['price_change'] = float(price_change[:percent_index])
        except:
            self.data['output']['price_change'] = ''

        class_name_title_keys = 'laHoVg'
        try:
            keys_list = extract_multi_item_by_class_name(class_name_title_keys)
            keys_list = [item.lower().replace(' (24h)','').replace('/','_').replace('.','_').replace(' ','_') for item in keys_list]
        
        except:
            keys_list = []
        try:
            class_name_title_values = 'hPHvUM'
            value_list = extract_multi_item_by_class_name(class_name_title_values)
            value_list = [remove_char_before_dollor(item) for item in value_list]
            value_list = [convert_to_numeric_values(item) for item in value_list]
        except:
            value_list = []
        
        # Convert lists to dictionary
        try:
            new_data = lists_to_dict(keys_list, value_list)

            # Add new data to the existing 'output' dictionary
            self.data['output'].update(new_data)
        except:
            pass


        class_name_rank_values = 'rank-value'  
        try:
            rank_value_list = extract_multi_item_by_class_name(class_name_rank_values)
            rank_value_list = [int(item.replace('#','')) for item in rank_value_list]
            self.data['output']['market_cap_rank'] = rank_value_list[0]
            self.data['output']['volume_rank'] = rank_value_list[1]
        except:
            self.data['output']['market_cap_rank'] = ''
            self.data['output']['volume_rank'] = ''

        # print(self.data)
        try:
            class_name_contract = 'dEZnuB'
            contract_name = extract_single_item_by_class_name(class_name_contract)
            class_name_address = 'address'
            address = extract_single_item_by_class_name(class_name_address)
            
            self.data['output']['Contracts'] =[{
                'name': contract_name.replace(': ',''),
                'address':address
            }]
        except:
            self.data['output']['Contracts'] =[]


        class_name_title_link = 'jTYLCR'
        title_link_elements = extract_multi_items_by_class_name(class_name_title_link)

        for title_link_element in title_link_elements:
            title_link_name = title_link_element.find_element(By.CLASS_NAME, 'fTGacL').text

            if title_link_name == 'Contracts':
                continue  # Skip Contracts info 
            if title_link_name == 'Network information':
                break # stop before Network information

            self.data['output'][title_link_name] =[]
            url_link_elements = title_link_element.find_elements(By.CLASS_NAME, 'gQoblf')
            
            for url_link in url_link_elements:
                name = url_link.text
                try:
                    a_element = url_link.find_element(By.LINK_TEXT, url_link.text)
                    url = a_element.get_attribute('href')
                except:
                    url = ''

                data = {
                    'name': name,
                    'url':url
                }
                self.data['output'][title_link_name].append(data)

        

    def close(self):
        self.driver.quit()

    def scrape(self):
        self.fetch_page()
        self.parse_data()
        self.close()
        return self.data

# CoinMarketCapScraper('duko')
# if __name__ == "__main__":
#     coin_acronym = "duko"  # Example coin acronym
#     scraper = CoinMarketCapScraper(coin_acronym)
#     data = scraper.scrape()
#     print(data)

