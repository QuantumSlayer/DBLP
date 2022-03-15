import requests
import re
import csv
from bs4 import BeautifulSoup

SEARCH_URL = "https://dblp.org/search/author"

class DBLP(object):
    
    def __init__(self):
        self.session = requests.Session()
        self.proxy = None
    
    def set_headers(self, headers):
        if headers:
            self.session.headers = headers

    def set_proxy(self, proxy):
        if proxy:
            self.proxy = {
                "http": proxy,
                "https": proxy
            }
    
    def _get_soup(self, *args, **kwargs):
        """
        Retrieve the website using get method in requests allowing proxy server.
        """
        if self.proxy:
            response = self.session.get(proxies=self.proxy, *args, **kwargs)
        else:
            response = self.session.get(*args, **kwargs)
        if response.status_code != 200:
            raise Exception("Failed to fetch webpage with status code " + str(response.status_code) + ". Please try again.")
        return BeautifulSoup(response.content, "lxml")
    
    def retrieve_from_search(self, query):
        """
        Search the name of the author and return a list of results.
        """
        params = {"q": query}
        res = self._get_soup(SEARCH_URL, params=params)
        author_list = res.find_all("a", href=re.compile("https://dblp.org/pid"))
        author = []
        if len(author_list):
            for entry in author_list:
                author.append((entry.get_text(), entry.get("href")))
            return author
        else:
            raise Exception("No matches for this name. Please try again.")
    
    def select_author(self, author):
        """
        Provide interactive selection from the author list.
        """
        num = len(author)
        print(str(num) + " author(s) found")
        for i, j in enumerate(author):
            print(str(i+1) + ": " + j[0] + ", link: " + j[1])
        select = int(input("Please select the author to download: "))
        if 1 <= select <= num:
            return author[select-1]
        else:
            raise Exception("Invalid value for selection. Please try again.")
    
    def download_list(self, author_link):
        """
        Generate a list of an author's papers with the link of that author.
        """
        response = self._get_soup(url=author_link)
        entry_list = response.find_all("cite", {"class": "data tts-content"})
        num = len(entry_list)
        print(str(num) + " paper(s) found.")
        paper_list = [0] * num
        for i, entry in enumerate(entry_list):
            text = entry.get_text()
            title = entry.find("span", {"class": "title"}).get_text()
            text = text.split(title, 1)
            authors = text[0][:-2]
            source = text[1][1:]
            paper_list[i] = [i+1, authors, title, source]
        return paper_list
    
    def write_to_csv(self, author, paper_list):
        """
        Write a list of papers into a csv file.
        """
        header = ["Number", "Authors", "Title", "Source"]
        filename = author + ".csv"
        with open(filename, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in paper_list:
                writer.writerow(row)
        print("List of articles saved to " + filename)