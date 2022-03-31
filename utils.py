import requests
import re
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
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
            return None
        return BeautifulSoup(response.content, "lxml")
    
    def retrieve_from_search(self, query):
        """
        Search the name of the author and return a list of results.
        """
        params = {"q": query}
        res = self._get_soup(SEARCH_URL, params=params)
        if not res:
            return -1
        author_list = res.find_all("a", href=re.compile("https://dblp.org/pid"))
        author = []
        if len(author_list):
            for entry in author_list:
                author.append((entry.get_text(), entry.get("href")))
            return author
        else:
            return 0
    
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
            return None
    
    def download_list(self, author_link):
        """
        Generate a list of an author's papers with the link of that author.
        """
        response = self._get_soup(url=author_link)
        if not response:
            return None
        entry_list = response.find_all("cite", {"class": "data tts-content"})
        num = len(entry_list)
        paper_list = [0] * num
        for i, entry in enumerate(entry_list):
            text = entry.get_text()
            title = entry.find("span", {"class": "title"}).get_text()
            text = text.split(title, 1)
            authors = text[0][:-2]
            source = text[1][1:]
            title = title[:-1]
            paper_list[i] = [i+1, authors, title, source]
        return paper_list
    
    def write_to_csv(self, author, paper_list, location=""):
        """
        Write a list of papers into a csv file.
        """
        header = ["Number", "Authors", "Title", "Source"]
        filename = author + ".csv"
        if not location:
            with open(filename, "w", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for row in paper_list:
                    writer.writerow(row)
            return filename
        else:
            with open(location, "w", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for row in paper_list:
                    writer.writerow(row)
            return location


class App(DBLP):

    def __init__(self, root):
        DBLP.__init__(self)
        frame = tk.Frame(root)
        root.title("DBLP Downloader")
        root.resizable(False, False)
        window_height = 480
        window_width = 480
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        self.canvas1 = tk.Canvas(root, width = window_width, height = window_height)
        self.canvas1.pack()

        self.entry1 = tk.Entry(root, width=54) 
        self.canvas1.create_window(255, 20, window=self.entry1)

        self.button1 = tk.Button(text='Search', command=lambda: App._search(self))
        self.canvas1.create_window(450, 20, window=self.button1)

        self.label1 = tk.Label(root, text='Input a name:')
        self.canvas1.create_window(50, 20, window=self.label1)

        self.label2 = tk.Label(root)
        self.canvas1.create_window(240, 42, window=self.label2)
        
        self.listbox1 = tk.Listbox(root, width=50, height=23)
        self.canvas1.create_window(240, 240, window=self.listbox1)

        self.button2 = tk.Button(text="Save", command=lambda: App._save(self))
        self.canvas1.create_window(240, 450, window=self.button2)

    def _search(self):
        self.label2.config(text="")
        self.listbox1.delete(0, tk.END)
        try:
            self.authors = DBLP.retrieve_from_search(self, self.entry1.get())
            if self.authors == -1:
                messagebox.showerror("Error", "Connection failed. Please try again.")
            elif self.authors == 0:
                self.label2.config(text="No matches for this name. Please try again.")
            else:
                self.label2.config(text = str(len(self.authors)) + " author(s) found. Please select the author(s) to download.")
                for i, j in enumerate(self.authors):
                    self.listbox1.insert(tk.END, str(i+1) + ": " + j[0])
        except:
            messagebox.showerror("Error", "Connection failed. Please try again.")
    
    def _save(self):
        try:
            entry = self.listbox1.get(self.listbox1.curselection()).split(":")
            num = int(entry[0]) - 1
            author = entry[1][1:]
            filename = filedialog.asksaveasfilename(initialfile=author, title="Save as", filetypes=[("Csv Files", "*.csv"), ('All Files', '*.*')], defaultextension="csv")
            if filename:
                paper_list = DBLP.download_list(self, self.authors[num][1])
                if not paper_list:
                    messagebox.showerror("Error", "Connection failed. Please try again.")
                else:
                    DBLP.write_to_csv(self, author, paper_list, location=filename)
                    messagebox.showinfo("Success", "File successfully saved to " + filename)
        except tk.TclError:
            messagebox.showerror("Error", "Nothing selected. Please try again.")
        except:
            messagebox.showerror("Error", "Connection failed. Please try again.")