from bs4 import BeautifulSoup
import requests

class Scraper():
    def __init__(self):
        self.pageContent = ""
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
          'referer':'https://www.zillow.com/homes/Missoula,-MT_rb/'}
        self.infoDict = {}

    def downloadPage(self, url):
        self.pageContent = requests.get(url, headers=self.headers).text

    def scrape(self, url):
        self.downloadPage(url)
        soup = BeautifulSoup(self.pageContent, "html.parser")

        try:
            #get overview 
            ovw = soup.find_all('span', class_='Text-c11n-8-84-0__sc-aiai24-0 dpf__sc-2arhs5-3 fsXIkY btxEYg')

            # Get title
            title = soup.title.text.strip()
            self.infoDict['title'] = title

            # Get price
            price_element = soup.find('span', class_='Text-c11n-8-84-0__sc-aiai24-0 dpf__sc-1me8eh6-0 hLAJE fzJCbY')
            self.infoDict['price'] = self.price = price_element.text.strip()

            # Get description
            desc = soup.find('div', class_='Text-c11n-8-84-0__sc-aiai24-0 sc-hiCibw fsXIkY hYphFd')
            self.infoDict['description'] = self.description = desc.text.strip()

            # Extracting facts and features section
            info_blocks = soup.select('.dpf__sc-1j9xcg4-0.gjalta')

            for block in info_blocks:
                heading = block.select_one('.StyledHeading-c11n-8-84-0__sc-ktujwe-0.gTVYcr').text
                items = block.select('.ListItem-c11n-8-84-0__sc-10e22w8-0.ddeTjq')

                for item in items:
                    label, value = item.select_one('span').text.split(':')
                    label = label.strip()
                    value = value.strip()
                    
                    if heading not in self.infoDict:
                        self.infoDict[heading] = {}
                    
                    self.infoDict[heading][label] = value

        except:
            pass




