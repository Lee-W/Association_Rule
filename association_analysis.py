import sys
from collections import Counter, OrderedDict
from itertools import groupby
from typing import List, Generator


def load_data(file_name: str) -> Generator[List[str], None, None]:
    with open(file_name, 'r') as input_file:
        data_gen = (line.split() for line in input_file.readlines())

        for _, group in groupby(data_gen, lambda x: x[0]):
            yield [item[2] for item in group]


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


def fp_growth(transactions: List[List[str]], min_support: int):
    counter = Counter()
    transactions = list(transactions)
    for trans in transactions:
        counter += Counter(trans)

    head_table = OrderedDict()
    non_frequent_items = set()
    for k, v in counter.most_common():
        if v < min_support:
            non_frequent_items.add(v)
        head_table[k] = v

    sorted_transcations = list()
    for trans in transactions:
        trans = filter(lambda x: x not in non_frequent_items, trans)
        sorted_transcations.append(
            sorted(trans, key=lambda x: counter[x], reverse=True)
        )

    tree = FpTree()
    for trans in sorted_transcations:
        tree.update_tree(trans)

    print(tree)
    print(tree.header_table)


class FpNode:
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = list()
        self.link = None

    def add_child(self, node):
        if self.has_child(node):
            index = self.children.index(node)
            self.children[index].count += 1
            child = self.children[index]
        else:
            self.children.append(node)
            child = self.children[-1]
        return child

    def has_child(self, node):
        return node in self.children

    def tree_str(self, level=0):
        ret = '   '*level + '{} ({})\n'.format(self.item, self.count)
        for child in self.children:
            ret += child.tree_str(level+1)
        return ret

    def __eq__(self, other):
        return self.item == other.item

    def __str__(self):
        return '{} ({})'.format(self.item, self.count)

    def __repr__(self):
        return self.__str__()


class FpTree:
    def __init__(self):
        self.root = FpNode('Null', 0, None)
        self.header_table = dict()

    def update_tree(self, transaction: List[str]):
        current = self.root

        for item in transaction:
            node = FpNode(item, 1, current)
            if not current.has_child(node):
                current = current.add_child(node)

                if item not in self.header_table:
                    self.header_table[item] = [current]
                else:
                    self.header_table[item].append(current)
            else:
                current = current.add_child(node)

    def __str__(self):
        return self.root.tree_str()


if __name__ == "__main__":
    transactions = load_data(sys.argv[1])
    fp_growth(transactions, 5)
