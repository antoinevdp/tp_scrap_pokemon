import os
import time
import requests
import boto3
from bs4 import BeautifulSoup

URL = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# S3 setup
s3 = boto3.client("s3")
BUCKET_NAME = "pokemonefrei"

def upload_to_s3(url, bucket, key):
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            s3.put_object(Bucket=bucket, Key=key, Body=r.content, ContentType="image/png")
            print(f"✅ Uploaded {key}")
        else:
            print(f"❌ Failed {url} (status {r.status_code})")
    except Exception as e:
        print(f"❌ Error uploading {url}: {e}")

def main():
    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find_all("table", {"class": "roundy"})

    for table in tables:
        rows = table.find_all("tr")[2:]  # Skip headers
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            # Name
            name_tag = cols[2].find("a")
            if not name_tag:
                continue
            name = name_tag.text.strip().replace(":", "").replace(" ", "_").replace("(", "").replace(")", "")

            # Image
            img_tag = cols[1].find("img")
            if not img_tag:
                continue
            src = img_tag["src"]
            if src.startswith("http"):
                img_url = src
            else:
                img_url = "https:" + src

            # Types
            types = [t.text.strip() for t in cols[3].find_all("a")]

            # Upload to S3 for each type
            for t in types:
                key = f"pokemon_images/{t}/{name}.png"
                upload_to_s3(img_url, BUCKET_NAME, key)
                time.sleep(0.5)  # be polite

if __name__ == "__main__":
    main()

