import typing


def generator(start: int, end: int) -> typing.Generator:
    if not isinstance(start, int) and not isinstance(end, int): raise TypeError()
    if start < 0 or (end < 0 or end < start): raise ValueError()
    
    for _ in range(start, end):
        yield _


from_1_to_5 = generator(start=1, end=5)
from_5_to_10 = generator(start=5, end=10)

def run_generator_step(generator: typing.Generator):
    try:
        return generator.send(None)
    except StopIteration as stop_iteration:
        return stop_iteration.value

while True:
    from_1_to_5_result = run_generator_step(generator=from_1_to_5)
    from_5_to_10_result = run_generator_step(generator=from_5_to_10)

    print(from_1_to_5_result) if from_1_to_5_result is not None else ...
    print(from_5_to_10_result) if from_5_to_10_result is not None else ...

    if from_1_to_5_result is None and from_5_to_10_result is None:
        break