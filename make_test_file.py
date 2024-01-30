from __future__ import annotations

import random
import json

from faker import Faker


def make_test_file():

    faker = Faker()

    test_file = './test.json'

    with open(test_file, 'w') as f:
        f.write('[')
        size = 10000000
        for i in range(size):
            item =  json.dumps({
                "id": i + 1,
                "title": faker.paragraph(nb_sentences=1),
                "rand_float": random.random(),
                "rand_int": random.randint(0, 1000000),
            }, indent=2)
            if i < size - 1:
                item += ',\n'
            f.write(item)
            print(f'{i + 1}/{size} ({round(((i + 1) / size) * 100, 1)}%)', end='\r')
        f.write(']')
        print()
        print('done')


if __name__ == '__main__':
    make_test_file()
