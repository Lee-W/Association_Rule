# implement aporiori algorithm with hash tree

import sys
from itertools import groupby, combinations
from operator import itemgetter, attrgetter
import pyfpgrowth

Transaction = []

MinSup = 0.3
MinConf = 0.7
# Transaction_count
N = 0
# FrequentItemSet
F = []
# FrequentItemSet with support
FreItemSet = {}
# Association_rule
Rule = []

class Candidate:
    def __init__(self, k):
        self.length = k
        self.candidate = []
        self.support = []
    def addCandidate(self, candidate):
        if candidate not in self.candidate:
            self.candidate.append(candidate)
            self.support.append(0)
    def addSupport(self, candidate = None, index = None):
        if index != None:
            self.support[index] = self.support[index] + 1
        elif candidate != None:
            if candidate in self.candidate:
                try:
                    index = self.candidate.index(candidate)
                    self.support[index] = self.support[index] + 1
                except:
                    print ('candidate index error')
            else:
                self.candidate.append(candidate)
                self.support.append(1)
        else:
            print ('wrong because candidate and index both none')
    def addAll(self, candidatesets):
        self.candidate = candidatesets
        length = len(self.candidate)
        for i in range(length):
            self.support.append(0)
    def extractFrequentSet(self):
        global N
        global MinSup
        returnSet = []
        returnCount = []
        for i,items in enumerate(self.candidate):
            if self.support[i] >= N * MinSup:
                returnSet.append(items)
                returnCount.append(self.support[i])

        return returnSet, returnCount
    def getNumOfCandidate(self):
        return len(self.candidate)
    def getOneCandidate(self, index):
        return self.candidate[index]
    def getAllCandidate(self) :
        return self.candidate
    def getAllNumber(self):
        return self.support

# The Hash Tree class, use the Hash Function: h(p) = p mod 3
class HashTree:
    def __init__(self, items, lenItem, level):
        self.length = lenItem
        self.items = items
        # Three sons
        self.leftChild = None
        self.midChild = None
        self.rightChild = None
        # the digital 0 stands for the first level
        self.buildTree(level)

    def buildTree(self, level):
        # the terminal condition
        if level == self.length - 1:
            # temp store the k-item
            tempbucket = []
            for subitem in self.items:
                prefixItem = subitem[:level]
                sufixItem = subitem[level:]
                for sitem in sufixItem:
                    #print ("sitem",sitem)
                    tempbucket.append(prefixItem + [sitem])
            ###|| It is also a big mistake, I used list(sitem) ago, and is will convert ths string '11' to ['1', '1']
            #print ("tempbucket",tempbucket)
            self.items = tempbucket

        else:
            # point the left , mid and right storage
            leftItems = []
            midItems = []
            rightItems = []

            for subitem in self.items:
                #print ("subitem",subitem)
                # get the number of the availale prefix item
                numPre = len(subitem) - self.length + 1
                #print ("numPre",numPre)
                ###|| It is big mistake, I added  " - level" ao
                # level: equals to the number of prefix
                for index in range(level, level+numPre):
                    # get the subitem. for example: abcd->abcd, bcd, cd
                    tempItem = subitem[:level] + subitem[index:]
                    #print (tempItem)
                    hashValue = int(subitem[index]) % 3
                    # hash to the different bucket
                    if hashValue == 0:
                        leftItems.append(tempItem)
                    elif hashValue == 1:
                        midItems.append(tempItem)
                    else:
                        rightItems.append(tempItem)
            # judge whether the list is empty or not
            if len(leftItems) != 0:
                self.leftChild = HashTree(leftItems, self.length, level + 1)
            if len(midItems) != 0:
                self.midChild = HashTree(midItems, self.length, level + 1)
            if len(rightItems) != 0:
                self.rightChild = HashTree(rightItems, self.length, level + 1)

    # judege the candidate whether belongs to the transacation or not
    def identifyCandidate(self, candidate, level):
        if self.length == level + 1:
            if candidate in self.items:
                return True
            else:
                return False
        else:
            hashvalue = int(candidate[level]) % 3


            if hashvalue == 0:
                if self.leftChild == None:
                    return False
                ###|| Forget the condition of no son
                return self.leftChild.identifyCandidate(candidate, level + 1)
            elif hashvalue == 1:
                if self.midChild == None:
                    return False
                return self.midChild.identifyCandidate(candidate, level + 1)
            else:
                if self.rightChild == None:
                    return False
                return self.rightChild.identifyCandidate(candidate, level + 1)

def subset(candidateSet, root):
    numCandidate = candidateSet.getNumOfCandidate()
    for index in range(numCandidate):
        level = 0
        if root.identifyCandidate(candidateSet.getOneCandidate(index), level):
            candidateSet.addSupport(None, index)

def load_data(file_name):
    with open(file_name, 'r') as input_file:
        data_gen = (line.split() for line in input_file.readlines())

        for _, group in groupby(data_gen, lambda x: x[0]):
            yield [item[2] for item in group]

def candiGen(itemsets, length):
    candidateset = []
    numItem = len(itemsets)

    for i in range(numItem-1):
        for j in range(i+1, numItem):
            tempCandidate = []
            if(length > 2):
                for y in range(length-1):
                    tempCandidate.append(itemsets[i][y])
                for x in range(length-1):
                    if itemsets[j][x] not in itemsets[i]:
                        tempCandidate.append(itemsets[j][x])

                if len(tempCandidate)==length:
                    tempCandidate.sort()
                    if tempCandidate not in candidateset:
                        candidateset.append(tempCandidate)
            else:
                tempCandidate.append(itemsets[i])
                tempCandidate.append(itemsets[j])
                C = sorted(tempCandidate, key=lambda x: int(x))
                if(len(tempCandidate)==length):
                    candidateset.append(C)

    return candidateset

def ruleGen(f, s):
    lenItem = len(f)
    lenSufix = len(s)
    prefixLine = list(set(f) - set(s))
    prefix = []

    if lenItem > lenSufix + 1:
        for obj in prefixLine:
            suffix = s.copy()
            suffix.append(obj)

            prefix = list(set(prefixLine)-set(obj))
            p = sorted(prefix, key=lambda x: int(x))
            conf = float(FreItemSet[tuple(f)]) / FreItemSet[tuple(p)]
            if conf >= MinConf:
                Rule.append([p, suffix, conf])
                ruleGen(f, s)

if __name__ == "__main__":
    data = load_data(sys.argv[1])
    #Transaction = list(data)
    Transaction = [
      ['6', '3', '1', '7', '8'],
      ['6', '3', '1', '2', '7'],
      ['6', '2'],
      ['3', '2', '8'],
      ['6', '3', '1', '7', '8']
      ]

    ## initial and generate C1(candidatesets) and L1(F[0])
    lenItem = 1
    candidateSet = Candidate(lenItem)
    for transaction in Transaction:
        N = N + 1
        for item in transaction:
            candidateSet.addSupport(item)

    candidatesets, setscount = candidateSet.extractFrequentSet()
    F.append(candidatesets) ## multi-layer list : store L1-Ln
    for i, item in enumerate(candidatesets):
        FreItemSet[tuple([item])] = setscount[i]

    # LOOP
    while True:
        lenItem = lenItem + 1
        candidateSet = Candidate(lenItem)
        candidateSet.addAll(candiGen(F[lenItem-2], lenItem))

        # Generate the Hash Tree
        for transaction in Transaction:
            templist = []
            templist.append(transaction)
            level = 0
            root = HashTree(templist, lenItem, level)
            subset(candidateSet, root)

        candidatesets, setscount = candidateSet.extractFrequentSet()

        if len(candidatesets) == 0:
            break

        F.append(candidatesets)
        for i, item in enumerate(candidatesets):
            l = sorted(item, key=lambda x: int(x))
            FreItemSet[tuple(l)] = setscount[i]

    #generate association rule
    '''
    count = 0
    for item in FreItemSet.items():
        print (item)
        count += 1
    print ("frequent_pattern_size",count)
    print ("Now let's generate rules")
    '''
    for k in range(len(F)-1,0,-1):
        for frequentItem in F[k]:
            for subItem in frequentItem:
                sufixRule = [subItem]
                prefixRule = list(set(frequentItem) - set(sufixRule))
                p = sorted(prefixRule, key=lambda x: int(x))
                conf = float(FreItemSet[tuple(frequentItem)]) / FreItemSet[tuple(p)]
                if conf >= MinConf:
                    Rule.append([p,sufixRule, conf])
                    ruleGen(frequentItem,sufixRule)
    '''
    print ("rule:")
    for rules in Rule:
        print (rules)
    '''
