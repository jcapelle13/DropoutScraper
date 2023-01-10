from bs4 import BeautifulSoup
import wget
import os
from sanitize_filename import sanitize

#TODO: Make use command line params?
filename = "file.html"
dest_dir = "imgs"

if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)

# Because i don't like with "with open() as f" blocks creating an indent
html_file = open(filename, 'r')

html = html_file.read()

soup = BeautifulSoup(html, 'html.parser')
for tag in soup.find_all('img'):
    filename = tag['alt']
    url = tag['src']
    # Strip off any extra query stuff, just get the file (limits scope admitedly)
    url = url.split('?')[0]
    # Get file Extension from url end
    #TODO: Add check for lack of extension?
    filename = filename + "." + url.split('.')[-1]
    filename = sanitize(filename)
    path = os.path.join(dest_dir, filename)
    if os.path.exists(path):
        print("Existing File found:", filename)
    else:
        print("Downloading", filename, "from", url)
        wget.download(url, path)


html_file.close()