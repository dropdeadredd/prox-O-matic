import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
from alive_progress import alive_bar

async def test_proxy(proxy):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://www.google.com", proxy=f"http://{proxy}") as response:
                response.raise_for_status()
                speed = response.elapsed.total_seconds() * 1000
                if speed < 5000:
                    return True
        except:
            pass
    return False

async def get_proxy_list(url, timeout=30):
    """
    This function returns a list of proxies that respond within a certain time limit.
    """

    NUMBER_OF_ATTRIBUTES = 8
    proxies = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as page:
                page.raise_for_status()

                soup = bs(await page.text(), 'lxml')
                table = soup.find('table')
                tbody = table.tbody if table else None

                if tbody:
                    infos = tbody.find_all('tr')
                    tasks = []
                    with alive_bar(len(infos)) as bar:
                        for info in infos:
                            proxy_data_temp = [i.text for i in info]
                            if len(proxy_data_temp) == NUMBER_OF_ATTRIBUTES:
                                proxy = f"{proxy_data_temp[0]}:{proxy_data_temp[1]}"
                                tasks.append(asyncio.ensure_future(test_proxy(proxy)))
                            bar()
                    results = await asyncio.gather(*tasks)
                    for i, result in enumerate(results):
                        if result:
                            proxies.append(p_format(*infos[i].stripped_strings))
                else:
                    print("Could not find proxy table")

    except Exception as e:
        print(f"\nFailed to get proxy list: {e}\nTry running the script again..")
        return None

    if proxies:
        with open('proxies.txt', 'w') as f:
            buffer = ""
            for proxy in proxies:
                buffer += f"{proxy[0]}:{proxy[1]}\n"
            f.write(buffer)

    return proxies

if __name__ == '__main__':
    urls = [
        "https://free-proxy-list.net/",
        "https://www.sslproxies.org/",
        "https://www.us-proxy.org/",
        "https://www.proxy-list.download/"
    ]

    proxies = []
    with alive_bar(len(urls)) as urls_bar:
        for url in urls:
            proxies += asyncio.run(get_proxy_list(url))
            urls_bar()
    if proxies:
        with open('proxies.txt', 'w') as f:
            buffer = ""
            for proxy in proxies:
                buffer += f"{proxy[0]}:{proxy[1]}\n"
            f.write(buffer)
