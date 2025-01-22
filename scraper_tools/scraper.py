from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import time
import os
from dotenv import load_dotenv

load_dotenv()

class Scraper():
    def __init__(self):
        self.df = None
        # Set Firefox options
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        #self.options.add_argument("--headless")  # headless mode if needed

        # Define the download directory
        self.download_dir = os.getenv('SRT_PATH')


        # Create the directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # Set up the Firefox profile
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("browser.download.folderList", 2)  # 2 means custom location
        self.profile.set_preference("browser.download.dir", self.download_dir)

        self.profile.set_preference("browser.download.useDownloadDir", True)
        
        #self.profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")  # Specify MIME types as needed
        self.profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain,application/octet-stream,application/x-subrip")

        
        # Add profile to options
        self.options.profile = self.profile

        # Initialize the Firefox driver with options
        self.driver = webdriver.Firefox(options=self.options)
        self.url = "https://tyler.caraza-harter.com/cs544/f24/schedule.html"


    def xpath_safe_click(self, xpath):
        attempts = 3
        for _ in range(attempts):
            try:
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                
                element.click()

                return  # Exit if successful
            except StaleElementReferenceException:
                pass  # Retry if stale
            except TimeoutError:
                pass


    def get_srt_file(self):
        self.xpath_safe_click('//*[@id="player-gui"]/div[3]/div[1]/div[3]/button')
        try:
            self.xpath_safe_click('//*[@id="player-gui"]/div[3]/div[2]/div[3]/div/div[3]/div/div/button')
        except:
            return None

        self.xpath_safe_click('//*[@id="player-gui"]/div[3]/div[1]/div[1]/div/div/div/div/div/div/div/div[2]')

        # Wait for file to appear in the download folder
        start_time = time.time()
        timeout = 30  # Max wait time
        downloaded_file = None

        while time.time() - start_time < timeout:
            # Get a list of .srt files in the download directory
            files = [f for f in os.listdir(self.download_dir) if f.endswith('.srt')]
                
            if files:
                # Get the most recently modified file
                newest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.download_dir, f)))
                downloaded_file = newest_file
                break

        return downloaded_file
        

    def get_date(self):
        # Locate and retrieve the text of the date
        date = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "js-entry-create-at"))
        ).find_element(By.TAG_NAME, "span").text

        return date


    def scrape_lecture_page(self, url):
        try:
            # Navigate to the URL
            self.driver.get(url)

            downloaded_file = self.get_srt_file()
            if not downloaded_file:
                return None

            date = self.get_date()

            embed_link = self.get_embed_link()

            # Return result if date and downloaded file are successfully retrieved
            if downloaded_file:
                return {
                    "file_name": os.path.join(self.download_dir, downloaded_file),
                    "date": date,
                    'embed_link': embed_link
                }
            else:
                raise FileNotFoundError("SRT file download timed out or failed.")

        finally:
            pass
            # self.driver.quit()


    def get_lessons(self, url):
        lecture_metadata = []

        # Refresh the page at the start of each retry
        self.driver.get(url)

        try:
            # Grab all lessons
            lessons = self.driver.find_elements(By.CSS_SELECTOR, 'div.col-md-4')
            
            # Filter for lessons containing a Kaltura lecture link
            lessons = [lesson for lesson in lessons if lesson.find_elements(By.CSS_SELECTOR, 'a[href*="https://mediaspace.wisc.edu"]')]

            # Extract metadata for each lesson with a Kaltura link
            lecture_metadata = [
                {
                    'title': lesson.find_element(By.TAG_NAME, 'h5').text,
                    'lecture_link': lesson.find_element(By.CSS_SELECTOR, 'a[href*="https://mediaspace.wisc.edu"]').get_attribute('href')
                }
                for lesson in lessons
            ]
            return lecture_metadata

        except Exception as e:
            return f'Error: {e}'


    def get_embed_link(self):
        """Retrieves the embed link from the page with retries and refreshes."""


        #self.id_safe_click('tab-share-tab')
        self.xpath_safe_click('/html/body/div/div[2]/div[5]/div/div[2]/div[4]/div[1]/div/div[1]/ul/li[2]/a/span')


        #self.id_safe_click('embedTextArea-pane-tab')
        #self.xpath_safe_click('//*[@id="embedTextArea-pane-tab"]')
        self.xpath_safe_click("/html/body/div/div[2]/div[5]/div/div[2]/div[4]/div[3]/div/div[2]/div/div/div[1]/ul/li[2]")


        # Wait for the embed text area to be present and retrieve the embed link
        embed_text_area = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="embedTextArea"]'))
        )
        embed_text = embed_text_area.get_attribute("value")
        return embed_text