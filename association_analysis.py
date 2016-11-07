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
    def __init__(self, suffix=None):
        self.root = FpNode(suffix, -1, None)
        self.header_table = dict()

    def build_tree(self, transactions, min_support):
        self.min_support = min_support

        self.find_frequent_item(transactions)

        for trans in transactions:
            trans = filter(lambda x: x in self.frequent_items, trans)
            sorted_trans = sorted(trans, key=lambda x: self.frequent_items[x], reverse=True)
            self.update_tree(sorted_trans)

    def find_frequent_item(self, transactions):
        counter = Counter()
        for trans in transactions:
            counter += Counter(trans)

        self.frequent_items = {k: v
                               for k, v in counter.most_common()
                               if v >= self.min_support}

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

    def mine_frequent_patterns(self):
        cond_pat_bases = dict()
        patterns = dict()
        for suffix, nodes in self.header_table.items():
            cpbs = list()
            for node in nodes:
                cpb = (list(), node.count)
                while node.parent != self.root:
                    node = node.parent
                    cpb[0].append(node)
                cpb[0].reverse()
                if cpb[0]:
                    cpbs.append(cpb)
            patterns.update(self.gen_combinations(suffix, cpbs))
        patterns.update({tuple(k): v for k, v in self.frequent_items.items()})
        patterns = {k: v for k, v in patterns.items() if v >= self.min_support}
        return patterns

    def gen_combinations(self, suffix, cpbs):
        patterns = defaultdict(int)
        for cpb, count in cpbs:
            for i in range(1, len(cpb)+1):
                for com in combinations(cpb, i):
                    patterns[tuple(sorted([item.item for item in com] + [suffix]))] += count
        return patterns

    def __str__(self):
        return self.root.tree_str()


if __name__ == "__main__":
    transactions = load_data(sys.argv[1])
    tree = FpTree()
    tree.build_tree(transactions, sys.argv[2])
    result = tree.mine_frequent_patterns()
