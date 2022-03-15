import argparse
from utils import *

def main():
    dblp = DBLP()

    parser = argparse.ArgumentParser(description="Enter the name of a computer scientist and download a list of all articles by that scientist from DBLP.")
    parser.add_argument("-he", "--headers", help="add header", type=str)
    parser.add_argument("-p", "--proxy", help="set up a proxy server address", type=str)
    parser.add_argument("-n", "--name", help="type the name of the author to search", type=str)

    args = parser.parse_args()

    if args.headers:
        dblp.set_headers(args.headers)
    if args.proxy:
        dblp.set_proxy(args.proxy)
    if args.name:
        authors = dblp.retrieve_from_search(args.name)
        author = dblp.select_author(authors)
        paper_list = dblp.download_list(author[1])
        dblp.write_to_csv(author[0], paper_list)


if __name__ == "__main__":
    main()