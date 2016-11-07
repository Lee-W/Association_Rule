import time
import sys
from itertools import groupby, combinations
from functools import wraps
from pprint import PrettyPrinter
import fpgrowth


def load_data(file_name: str):
    with open(file_name, 'r') as input_file:
        data_gen = (line.split() for line in input_file.readlines())

        for _, group in groupby(data_gen, lambda x: x[0]):
            yield [item[2] for item in group]


def timefunc(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end-start)
        return result
    return wrapper


def export_weka_arff(transactions, file_name: str, item_num: int):
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


@timefunc
def find_frequent_patterns(transactions, min_support, *, algorithm='fpgrowth'):
    if algorithm == 'fpgrowth':
        return fpgrowth.find_frequent_patterns(transactions, min_support)
    elif algorithm == 'hashtree':
        pass


@timefunc
def generate_association_rules(patterns, min_confidence):
    rules = {}
    for itemset in patterns.keys():
        itemset_support = patterns[itemset]
        for i in range(1, len(itemset)):
            for com in combinations(itemset, i):
                cause = tuple(sorted(com))
                effect = tuple(sorted(set(itemset) - set(cause)))

                if cause in patterns:
                    confidence = itemset_support / patterns[cause]

                    if confidence >= min_confidence:
                        rules[tuple([cause, effect])] = confidence
    return rules


if __name__ == "__main__":
    pp = PrettyPrinter(indent=4)

    file_name, min_support, min_confidence = sys.argv[1:]
    transactions = list(load_data(file_name))
    transactions_num = len(transactions)
    patterns = find_frequent_patterns(transactions, float(min_support)*transactions_num)
    rules = generate_association_rules(patterns, float(min_confidence))

    print('-------pattern--------')
    pp.pprint(patterns)
    print('-------rule--------')
    pp.pprint(rules)
