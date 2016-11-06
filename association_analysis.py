import sys
from collections import Counter
from itertools import groupby
from typing import List, Generator


def load_data(file_name: str) -> Generator[List[str], None, None]:
    with open(file_name, 'r') as input_file:
        data_gen = (line.split() for line in input_file.readlines())

        for _, group in groupby(data_gen, lambda x: x[0]):
            yield [item[2] for item in group]


def fp_growth(transactions: List[List[str]], min_support: int):
    counter = Counter()
    for trans in transactions:
        counter += Counter(trans)

    for k, v in counter.most_common():
        if v < min_support:
            break
        print(k, v)


def export_weka_arff(transactions: List[List[str]], file_name: str, item_num: int):
    with open(file_name, 'w') as output_file:
        output_file.write("@relation 'IBM data'\n")
        for i in range(item_num):
            output_file.write('@attribute {} {{F, T}}\n'.format(i))
        output_file.write('@data\n')

        for trans in transactions:
            output_file.write('{')
            output_file.write('{} T'.format(trans[0]))

            for item in trans[1:]:
                output_file.write(' ,{} T'.format(item))

            output_file.write('}\n')


if __name__ == "__main__":
    data = load_data(sys.argv[1])

    export_weka_arff(data, 'hi.arff', 100)
