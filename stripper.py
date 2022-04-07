from bs4 import BeautifulSoup
import wget

filename = "file.html"

html_file = open(filename, 'r')

html = html_file.read()

soup = BeautifulSoup(html, 'html.parser')
for tag in soup.find_all('img'):
    filename = tag['alt']
    url = tag['src']
    url = url.split('?')[0]
    filename = filename + "." + url.split('.')[-1]
    wget.download(url, filename)


html_file.close()