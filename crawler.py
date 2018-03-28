import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def read_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as content:
            return await content.text()


def is_valid_href(href):
    black_list = ['.com', '.pdf']
    if not href:
        return False
    if href == '/' or not href[0] == '/':
        return False
    for bad in black_list:
        if bad in href:
            return False
    return True


def find_urls(domain, content):
    result = []
    soup = BeautifulSoup(content, 'lxml')
    for link in soup.findAll('a'):
        href = link.get('href')
        if is_valid_href(href):
            url = 'https://{}{}'.format(domain, href).strip('/')
            result.append(url)
    return result


async def crawler(domain, uid):
    while True:
        current = await q.get()
        print(current)
        content = await read_url(current)
        for url in find_urls(domain, content):
            if not url in seen:
                seen.add(url)
                q.put_nowait(url)
        q.task_done()


async def run(n, domain):
    tasks = []
    for uid in range(n):
        task = asyncio.ensure_future(crawler(domain, uid))
        tasks.append(task)
    await q.join()
    for task in tasks:
        task.cancel()


if __name__ == '__main__':
    domain = 'nbc.com'
    seen = set()
    num_workers = 30
    q = asyncio.Queue()
    q.put_nowait('https://{}'.format(domain))
    seen.add(domain)
    event_loop = asyncio.get_event_loop()
    run = event_loop.run_until_complete(run(num_workers, domain))
    event_loop.close()