import asyncio
import time


# async is used to define a "coroutine"
async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


# another coroutine.
async def main():
    task1 = asyncio.create_task(
        say_after(2, 'hello'))

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    # run two coroutines "concurrently"
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")

if __name__ == '__main__':
    asyncio.run(main())


