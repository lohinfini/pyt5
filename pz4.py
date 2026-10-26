import aiohttp
import asyncio
import json
from datetime import datetime

BRANDS_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetAllMakes?format=json"
VEHICLE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetVehicleTypesForMakeId/440?format=json"

semaphore = asyncio.Semaphore(3)


async def fetch_data(url, session):
    async with semaphore:
        for attempt in range(3):
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()

                    print(f"Ошибка запроса: {response.status}")

            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Ошибка запроса: {e}")

            if attempt < 2:
                await asyncio.sleep(1)

    return None


async def get_car_data():
    async with aiohttp.ClientSession() as session:
        brands_task = fetch_data(BRANDS_URL, session)
        types_task = fetch_data(VEHICLE_URL, session)

        brands, vehicle_types = await asyncio.gather(
            brands_task, types_task
        )

        return {
            "brands": brands,
            "vehicle_types": vehicle_types,
            "timestamp": datetime.now().isoformat()
        }


def save_data(data):
    with open("cars.json", "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


async def main():
    while True:
        data = await get_car_data()

        if data:
            save_data(data)
            print("Данные сохранены в cars.json")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("Не удалось получить данные")

        await asyncio.sleep(600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа остановлена")