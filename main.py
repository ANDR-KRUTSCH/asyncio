import os, pathlib, time, functools, asyncio
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.sharedctypes import Value
from multiprocessing.sharedctypes import Synchronized
from typing import Generator


def delete_file():
    os.remove(path=pathlib.Path(__file__).resolve().parent / 'digits.txt')

def create_file(number_of_rows: int) -> None:
    try:
        with open(file='digits.txt', mode='x') as file:
            rows = [f'{row}\t{row}\t{row}\t{row}\n' for row in range(1, number_of_rows + 1)]
            file.writelines(rows)
    except FileExistsError:
        delete_file()
        create_file(number_of_rows=number_of_rows)

map_progress: Synchronized

def init(progress: Synchronized) -> None:
    global map_progress
    map_progress = progress

def partition(data: list[str], chunk_size: int) -> Generator:
    for _ in range(0, len(data), chunk_size): yield data[_ : _ + chunk_size]

def map_frequencies(chunk: list[str]) -> dict[str, int]:
    counter = dict()
    for line in chunk:
        word, _, count, _ = line.replace('\n', '').split('\t')
        if counter.get(word):
            counter[word] = counter[word] + int(count)
        else:
            counter[word] = int(count)

    with map_progress.get_lock():
        map_progress.value += 1

    return counter

def progress_reporter(total_partitions: int) -> None:
    while map_progress.value < total_partitions:
        print(f'Finished: {map_progress.value}/{total_partitions}')
        time.sleep(1)
    print(f'Finished: {map_progress.value}/{total_partitions}')

# async def progress_reporter(total_partitions: int) -> None:
#     while map_progress.value < total_partitions:
#         print(f'Finished: {map_progress.value}/{total_partitions}')
#         await asyncio.sleep(1)
#     print(f'Finished: {map_progress.value}/{total_partitions}')

def merge_dicts(first: dict[str, int], second: dict[str, int]) -> dict[str, int]:
    merge = first
    for key in second:
        if key in merge:
            merge[key] = merge[key] + second[key]
        else:
            merge[key] = second[key]
    return merge

async def main(partition_size: int) -> None:
    create_file(number_of_rows=10000000)
    
    global map_progress

    with open(file='digits.txt') as file:
        contents = file.readlines()

        map_progress = Value('i', 0)
        tasks = list()
        loop = asyncio.get_running_loop()

        start = time.time()

        with ProcessPoolExecutor(initializer=init, initargs=(map_progress, )) as pool:
            total_partitions = len(contents) // partition_size

            tasks.append(loop.run_in_executor(executor=pool, func=functools.partial(progress_reporter, total_partitions)))

            # reporter = asyncio.create_task(coro=progress_reporter(total_partitions=total_partitions))
            
            for chunk in partition(data=contents, chunk_size=partition_size): tasks.append(loop.run_in_executor(executor=pool, func=functools.partial(map_frequencies, chunk)))

        counters = await asyncio.gather(*tasks)
        
        counters.pop(counters.index(None))

        # await reporter

        final_result = functools.reduce(merge_dicts, counters)

        print('60: {}'.format(final_result['60']))

        end = time.time()

        print(f'{end - start:.3f}')
    
    # delete_file()


if __name__ == '__main__':
    asyncio.run(main=main(partition_size=500000))