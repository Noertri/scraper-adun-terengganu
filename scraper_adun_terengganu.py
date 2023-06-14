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
    souped = BeautifulSoup(r.text, "lxml")
    table = souped.select_one("article table")

    sentene_pattern = re.compile(r"[\w\s,]+?\n([\w\s',\.]+)\n([\w\s\(\)]+)")

    results = list()

    if table:
        rows = table.select("tr")
        if rows:
            for row in rows:
                for col in row.select("td"):
                    result = {"position": "Member of the State Legislative Assembly (Ahli Dewan Undangan Negeri) | State Legislative Assembly (Dewan Undangan Negeri), Terengganu"}
                    c = col.get_text(strip=True, separator="\n")
                    if (c := sentene_pattern.match(c)):
                        result["name"] = c.group(1).replace("\n", " ")
                        result["address"] = c.group(2).replace("\n", "")
                        result["photo_link"] = parse.urljoin(main_url, parse.quote(src)) if (src := col.select_one("img").get("src", None)) else ""
                        results.append(result)

    if not os.path.isdir("hasil"):
        os.makedirs("hasil")

    filename = "ADUN_Terengganu_{0}.csv".format(datetime.now().strftime("%d%m%Y%H%M%S"))

    print(f"Save to hasil/{filename}...")

    try:
        with open(os.path.join("hasil", filename), "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("name", "position", "address", "photo_link"))
            writer.writeheader()
            writer.writerows(results)
            f.close()
            print("Done...")
    except Exception as err:
        traceback.print_exc()


if __name__ == "__main__":
    with httpx.Client(follow_redirects=True, verify=False) as client:
        scraper(cl=client)
