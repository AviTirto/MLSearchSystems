from scraper import Scraper
from lecture_parser import Parser
import os, shutil

folder = '../raw_srt_files'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))


s = Scraper()
# p = Parser()

lessons = s.get_lessons("https://tyler.caraza-harter.com/cs544/f24/schedule.html")

for lesson in lessons:
    file_metadata = s.scrape_lecture_page(lesson['lecture_link'])
    try:
        filename = file_metadata['file_name']
        print(filename)
    except:
        pass