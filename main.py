import argparse
from utils import *
PROXY = ""
# PROXY = "http://127.0.0.1:7890"

def main():
    dblp = DBLP()

    parser = argparse.ArgumentParser(description="Enter the name of a computer scientist and download a list of all articles by that scientist from DBLP.")
    parser.add_argument("-he", "--headers", help="add header", type=str)
    parser.add_argument("-p", "--proxy", help="set up a proxy server address", type=str)
    parser.add_argument("-n", "--name", help="type the name of the author to search", type=str)

    args = parser.parse_args()

    if not args.name:
        root = tk.Tk()
        ap = App(root)
        ap.set_proxy(PROXY)
        root.mainloop()
    else:
        if args.headers:
            dblp.set_headers(args.headers)
        if args.proxy:
            dblp.set_proxy(args.proxy)
        if args.name:
            authors = dblp.retrieve_from_search(args.name)
            if authors == -1:
                raise Exception("Connection failed. Please try again.")
            elif authors == 0:
                raise Exception("No matches for this name. Please try again.")
            else:
                author = dblp.select_author(authors)
            if not author:
                raise Exception("Invalid value for selection. Please try again.")
            paper_list = dblp.download_list(author[1])
            if not paper_list:
                raise Exception("Connection failed. Please try again.")
            else:
                dblp.write_to_csv(author[0], paper_list)

if __name__ == "__main__":
    main()