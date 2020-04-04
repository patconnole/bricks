#!/usr/bin/env python3.7

from itertools import accumulate,islice
from math import factorial
from collections import deque
import array
from time import monotonic

def get_combos(a,b,w):
    retval = []
    max_a_count = w // a
    for a_count in range(max_a_count +1):
        b_count,r = divmod(w - a_count*a, b)
        if r == 0:
            retval.append([a]*a_count + [b]*b_count)
    return retval

def get_permutation_count(brick_combos):
    answer = 0
    for combo in brick_combos:
        count_map = {}
        for value in combo:
            if value in count_map.keys():
                count_map[value] +=1
            else:
                count_map[value] = 1
        denom = 1
        for key in count_map.keys():
            denom *= factorial(count_map[key])
        answer += factorial(len(combo)) // denom
    return answer

def yield_brick_permutations(brick_combos):
    for brick_combo in brick_combos:
        yield from _get_unique_perms_of_combo(brick_combo)

def _get_unique_perms_of_combo(brick_combo):
    if len(brick_combo) < 2:
        yield brick_combo
    else:
        for unique_brick in set(brick_combo):
            b = brick_combo.copy()
            b.remove(unique_brick)
            for perm in _get_unique_perms_of_combo(b):
                yield [unique_brick]+perm

def yield_brick_seams(brick_combos):
    for perm in yield_brick_permutations(brick_combos):
        yield set([*accumulate(perm)][:-1])

def yield_seam_graph_nodes(brick_combos):
    count = 0
    for a_node in yield_brick_seams(brick_combos):
        retval = array.array('H')
        b_iter = yield_brick_seams(brick_combos)
        consume(b_iter,count)
        for i_b, b_node in enumerate(b_iter):
            if a_node.isdisjoint(b_node):
                retval.append(i_b + count)
        yield retval
        count +=1

def consume(iterator, n=None):
    if n is None:
        deque(iterator, maxlen=0)
    else:
        next(islice(iterator, n, n), None)

class _Matrix():
    def __init__(self, size):
        self.data = []
        self.size = size
        for i in range(size):
            self.data.append(array.array('H', (0 for _ in range(self.size - i))))
    def __repr__(self):
        retval = ''
        if self.size > 40:
            return 'too big to print matrix'
        for i in range(self.size):
            space = i*3
            spacer = ' '*space
            retval += spacer + str(self.data[i].tolist()) + '\n'
        return retval
    def get_count(self):
        retval = 0
        for i_row in range(self.size):
            for i_col in range(self.size - i_row):
                if i_col == 0:
                    retval += self.data[i_row][i_col]
                else:
                    retval += 2* self.data[i_row][i_col]
        return retval
    def __matmul__(self,other):
        size = self.size
        _range = range
        retval = Matrix(size)
        selfdata = self.data
        otherdata = other.data
        retvaldata = retval.data
        for i_row in _range(size):
            now = monotonic()
            selfdata_irow = selfdata[i_row]
            retvaldata_row = retvaldata[i_row]
            #print(i_row, ' of ', size)
            for i_col in _range(i_row,size):
                otherdata_icol = otherdata[i_col]
                cell = 0
                for i in _range(size):
                    if i_row > i:
                        if i_col > i:
                            cell += selfdata[i][i_row - i] * otherdata[i][i_col - i]
                        else:
                            cell += selfdata[i][i_row - i] * otherdata_icol[i - i_col]
                    else:
                        if i_col > i:
                            cell += selfdata_irow[i - i_row] * otherdata[i][i_col - i]
                        else:
                            cell += selfdata_irow[i - i_row] * otherdata_icol[i - i_col]
                retvaldata_row[i_col - i_row] = cell
            print(i_row, monotonic() - now)

        return retval

    
class AdjacencyMatrix(_Matrix):
    def __init__(self, size, gen):
        super().__init__(size)
        self._ingest(gen)
    def _ingest(self, gen):
        for i,row in enumerate(gen):
            for item in row:
                self.data[i][item -i] = 1

class Matrix(_Matrix):
    def __init__(self,size):
        super().__init__(size)

def mulitply_matrix(am, height):
    retval = am
    for i in range(height-1):
        print('multiplying..', i)
        retval = retval @ am
    return retval.get_count()



def run(a,b,w,h):
    combos = get_combos(a,b,w)
    
    perm_count = get_permutation_count(combos)
    print('perm_count', perm_count)
    am = AdjacencyMatrix(perm_count,yield_seam_graph_nodes(combos))
    print(am)
    print(mulitply_matrix(am,h-1))

if __name__ == '__main__':
    a,b = 2,3
    w = 32
    h =3
    run(a,b,w,h)
