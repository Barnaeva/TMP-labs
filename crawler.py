import asyncio
import aiohttp
import gzip
import csv
import json


INPUT_CSV = "top-10k.csv.gz"
JSON = "domain_status.json"
MAX_CONNECTIONS = 1000


def read_csv(filename):
    domains = []
    with gzip.open(filename, mode="rt", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            domains.append(row[0])
    return domains


async def fetch(session, url):
    try:
        async with session.get(url) as resp:
            body = await resp.read()
            lang = resp.headers.get("Content-Language")
            content_language = lang.split(",") if lang else []
            cookies = list(resp.cookies.keys())

            return {
                "status": resp.status,
                "server": resp.headers.get("Server"),
                "length": len(body),
                "language": content_language,
                "cookies": cookies,
                "error": None
            }

    except Exception as e:
        return {
            "status": None,
            "server": None,
            "length": None,
            "language": [],
            "cookies": [],
            "error": str(e)
        }


async def check_domain(session, domain):
    result = {
        "domain": domain,

        "http_status": None,
        "http_server": None,
        "http_content_length": None,
        "http_content_language": [],
        "http_cookies": [],

        "https_status": None,
        "https_server": None,
        "https_content_length": None,
        "https_content_language": [],
        "https_cookies": []
    }

    http = await fetch(session, f"http://{domain}")

    result["http_status"] = http["status"]
    result["http_server"] = http["server"]
    result["http_content_length"] = http["length"]
    result["http_content_language"] = http["language"]
    result["http_cookies"] = http["cookies"]

    https = await fetch(session, f"https://{domain}")

    result["https_status"] = "Ok" if not https["error"] else https["error"]
    result["https_server"] = https["server"]
    result["https_content_length"] = https["length"]
    result["https_content_language"] = https["language"]
    result["https_cookies"] = https["cookies"]

    return result


async def main():
    domains = read_csv(INPUT_CSV)

    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)

    async with aiohttp.ClientSession(
        headers={ "Accept-Language": "ru-RU" },
        connector=connector
    ) as session:

        tasks = []
        for domain in domains:
            tasks.append(check_domain(session, domain))

        results = await asyncio.gather(*tasks)

    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
