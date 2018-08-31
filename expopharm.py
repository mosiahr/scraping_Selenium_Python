from selenium import webdriver
import re
import csv
import time
from random import uniform


BASE_URL = 'http://expopharm.eu/visitors/list-of-exhibitors/'
FILE = 'expopharm.csv'
FIELDS = (
    'Url', 'Name', 'Address', 'City', 'Country', 'Phone', 'Website', 'Email',
    'Category1', 'SubCategory1',
    'Category2', 'SubCategory2',
    'Category3', 'SubCategory3',
)


class Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Firefox()
        self.scrap(self.url)

    def scrap(self, url):
        self.driver.get(url)
        time.sleep(uniform(8, 10))

        # click no the button cookie
        self.driver.find_element_by_css_selector('a.cookie_action_close_header').click()
        # time.sleep(uniform(3, 5))

        # click on the button(paginator)
        while True:
            button = self.driver.find_element_by_css_selector('button.gwt-Button.OB0JQR-f-i')
            if button.is_displayed():
                button.click()
                time.sleep(uniform(2, 3))
            else:
                break

        # Save title
        self.save_csv(FIELDS, FILE)

        while True:
            try:
                rez_cat = []

                # item scroll into down
                self.driver.execute_script("document.querySelector('div.OB0JQR-l-B.OB0JQR-l-F').scrollIntoView(top=false)")

                # click on the item
                self.driver.find_element_by_css_selector('div.OB0JQR-l-B.OB0JQR-l-F').click()
                # time.sleep(uniform(1, 2))

                # scraping
                try:
                    url = self.driver.current_url
                except:
                    url = None

                print("Scrape: ", url)

                try:
                    name = self.driver.find_element_by_css_selector("div.gwt-Label[itemprop='legalName']").text.strip()
                except:
                    name = None

                try:
                    address = self.driver.find_element_by_css_selector("div[itemprop='streetAddress']")
                    address = address.find_element_by_css_selector("div.gwt-Label.OB0JQR-b-xb.OB0JQR-b-oc").text.strip()
                except:
                    address = None

                try:
                    city = self.driver.find_element_by_css_selector("span.gwt-InlineLabel[itemprop='addressLocality']").text.strip()
                except:
                    city = None

                try:
                    country = self.driver.find_element_by_css_selector("div.gwt-Label[itemprop='addressCountry']").text.strip()
                except:
                    country = None

                try:
                    telephone = self.driver.find_element_by_css_selector("div.gwt-Label[itemprop='telephone']").text.strip()
                except:
                    telephone = None

                try:
                    website = self.driver.find_element_by_css_selector("a.gwt-Anchor[itemprop='url']").text.strip()
                except:
                    website = None

                try:
                    email = self.driver.find_element_by_css_selector("a.gwt-Anchor[itemprop='email']").text.strip()
                except:
                    email = None

                try:
                    categories = self.driver.find_elements_by_css_selector("div.OB0JQR-c-r")
                    for category in categories:
                        category.click()
                        # time.sleep(uniform(2, 3))

                        try:
                            category = category.get_attribute('title')
                        except:
                            category = None

                        sub_arr = []
                        subs = self.driver.find_elements_by_css_selector('div.OB0JQR-b-n')
                        for s in subs:
                            try:
                                if re.match(r'^[0-9].[0-9][a-zA-Z\s]+', s.find_element_by_css_selector('div.gwt-Label').text):
                                    sub = s.find_element_by_css_selector('div.gwt-Label').text
                                    sub_arr.append(sub)
                            except:
                                pass

                        rez_cat.append({
                                'category': category,
                                'sub': ', '.join(sub_arr)
                            })

                except Exception as e:
                    print(e)

                rez_item = {
                    'url': url,
                    'name': name,
                    'address': address,
                    'city': city,
                    'country': country,
                    'telephone': telephone,
                    'website': website,
                    'email': email,
                    'rez_cat': rez_cat,
                }

                # Save row
                self.save_one_row(rez_item, FILE)

                # close item
                self.driver.find_element_by_css_selector('div.OB0JQR-c-ec.OB0JQR-b-w').click()
                # time.sleep(uniform(2, 3))

                # remove item
                self.driver.execute_script("document.querySelector('div.OB0JQR-l-B.OB0JQR-l-F').remove()")
                # time.sleep(uniform(2, 3))

            except Exception as e:
                print(e)
                break

    def save_csv(self, row_fields, path_to_file, mode='w'):
        with open(path_to_file, mode) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row_fields)

    def save_one_row(self, data, path):
        with open(path, 'a') as csvfile:
            writer = csv.writer(csvfile)
            row = (
                (data['url']),
                (data['name']),
                (data['address']),
                (data['city']),
                (data['country']),
                (data['telephone']),
                (data['website']),
                (data['email']),
            )
            if data['rez_cat'] is not None:
                for i in range(0, len(data['rez_cat'])):
                    row += (data['rez_cat'][i]['category'],)
                    if data['rez_cat'][i]['sub'] is not None:
                        row += (data['rez_cat'][i]['sub'],)
                    else:
                        row += ''

            writer.writerow(row)


if __name__ == '__main__':
    start = time.time()
    scraper = Scraper(BASE_URL)
    print("Time run: ", time.time() - start)