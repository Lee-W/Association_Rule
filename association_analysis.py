import sys
from itertools import groupby


def load_data(file_name):
    with open(file_name, 'r') as input_file:
        data_gen = (line.split() for line in input_file.readlines())

        for _, group in groupby(data_gen, lambda x: x[0]):
            yield [item[2] for item in group]


if __name__ == "__main__":
    data = load_data(sys.argv[1])
    # TODO: implement aporiori algorithm
