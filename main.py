import asyncio
import re
import aiohttp

async def fetch_usernames(session, params, output_file):
    url = f"https://www.roblox.com/avatar-thumbnails?params=[{params}]"
    usernames = {}

    try:
        async with session.get(url, allow_redirects=False) as response:
            if response.status == 200:
                data = await response.text()
                users = re.findall(r'"id":(\d+?),"name":"(.+?)",', data)
                for u_id, u_name in users:
                    usernames[int(u_id)] = u_name
            else:
                print(f"Failed to fetch data for batch with params: {params}")
    except Exception as e:
        print(f"Error fetching data: {e}")

    for user_id, username in sorted(usernames.items()):
        output_file.write(f"{user_id}:{username}\n")
    output_file.flush()

async def main2():
    max_user_id = 100000
    start_user_id = 1

    batch_size = 50
    batch_limit = 10
    delay_seconds = 20 

    output_file = open("users.txt", "a", encoding="UTF-8")

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'}) as session:
        tasks = []
        for i in range(start_user_id, max_user_id, batch_size):
            if len(tasks) >= batch_limit:
                await asyncio.gather(*tasks)
                tasks = []
                print("WAITING")
                # await asyncio.sleep(delay_seconds)
            params = ','.join(f'{{"userid":"{str(i + j)}"}}' for j in range(batch_size))
            tasks.append(fetch_usernames(session, params, output_file))

        if tasks:
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main2())
