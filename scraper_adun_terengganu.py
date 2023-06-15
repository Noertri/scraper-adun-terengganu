import httpx
from bs4 import BeautifulSoup
from urllib import parse
import re
from datetime import datetime
import os
import csv
import traceback


main_url = "https://dun.terengganu.gov.my"


def scraper(cl: httpx.Client):
    print("Start to scrape web...")
    r = cl.get(parse.urljoin(main_url, "index.php/2013-06-26-00-46-38/ahli-dewan-undangan-negeri"), timeout=5.)
    souped = BeautifulSoup(r.text, "html.parser")
    table = souped.select_one("article table")

    split_pattern = re.compile(r"[\n\r\t]+")
    nbsp_pattern = re.compile(r"(\xa0{1,})")
    non_ascii = re.compile(r"[^\x20-\x7F]+")

    results = list()

    if table:
        rows = table.select("tr")
        if rows:
            for row in rows:
                for col in row.select("td"):
                    result = {"position": "Member of the State Legislative Assembly (Ahli Dewan Undangan Negeri) | State Legislative Assembly (Dewan Undangan Negeri), Terengganu"}
                    c = col.get_text().strip()
                    if bool(c):
                        words = [nbsp_pattern.sub(" ", non_ascii.sub("'", word)) for word in split_pattern.split(c)]
                        result["name"] = " ".join(words[:-1])
                        result["address"] = words[-1]
                        result["photo_link"] = parse.urljoin(main_url, parse.quote(src)) if (src := col.select_one("img").get("src", None)) else ""
                        results.append(result)

    if not os.path.isdir("results"):
        os.makedirs("results")

    filename = "ADUN_Terengganu_{0}.csv".format(datetime.now().strftime("%d%m%Y%H%M%S"))

    print(f"Save to results/{filename}...")

    try:
        with open(os.path.join("results", filename), "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("name", "position", "address", "photo_link"), delimiter=";")
            writer.writeheader()
            writer.writerows(results)
            f.close()
            print("Done...")
    except Exception as err:
        traceback.print_exc()


if __name__ == "__main__":
    with httpx.Client(follow_redirects=True, verify=False) as client:
        scraper(cl=client)
