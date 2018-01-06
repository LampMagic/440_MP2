import numpy as np
import time
import math
import copy
import random


def read_puzzles(textPuzzles):
    file = open(textPuzzles,'r')
    text = file.read()
    line = text.splitlines()
    return np.asarray([list(x) for x in line])


def print_puzzles(puzzles):
    print("\nPrinting raw puzzle")
    print("rc0123456789")
    i = 0
    for line in puzzles:
        print(i,''.join(line))
        i += 1
    print("\n")


def print_solution(solution):
    print("\nPrinting solution")
    print("rc0123456789")
    i = 0
    for i in range(solution.shape[0]):
        print(i,'',end="")
        for j in range(solution.shape[1]):
            cur = solution[i,j]
            print(chr(cur),end="")
        print('')

    
def build_Start_State(rawPuzzle):
    # construcing a 2d array
    output = np.zeros((rawPuzzle.shape[0],rawPuzzle.shape[1]),dtype=np.uint8)
    source = []
    value = []
    for row in range(rawPuzzle.shape[0]):
        for col in range(rawPuzzle.shape[1]):
            if rawPuzzle[row,col] != '_':
                # [color]
                output[row,col] = ord(rawPuzzle[row,col])
                # [i,j,color] 
                source.append([row,col,output[row,col]])
                if output[row,col] not in value:
                    # [color]
                    value.append(output[row,col])
    return output,source,value

#########################################
def neighbour(location,state):
    output = []
    if location[0]>0:
        output.append(state[location[0]-1,location[1]])

    if location[0]<state.shape[1]-1:
        output.append(state[location[0]+1,location[1]])

    if location[1]>0:
        output.append(state[location[0],location[1]-1])

    if location[1]<state.shape[0]-1:
        output.append(state[location[0],location[1]+1])

    return output

def find_neighbor(state,cur):
    row = cur[0]
    col = cur[1]
    zero = []
    nonzero = []
    # bottom neighbor
    if row < state.shape[0]-1:
        if state[row+1,col] != 0:
            # [color]
            nonzero.append(state[row+1,col])
        else:
            # [row,col]
            zero.append([row+1,col])
    # top neighbor
    if row > 0:
        if state[row-1,col] != 0:
            nonzero.append(state[row-1,col])
        else:
            zero.append([row-1,col])
    # right neighbor
    if col < state.shape[1]-1:
        if state[row,col+1] != 0:
            nonzero.append(state[row,col+1])
        else:
            zero.append([row,col+1])
    # left neighbor
    if col > 0:
        if state[row,col-1] != 0:
            nonzero.append(state[row,col-1])
        else:
            zero.append([row,col-1])    
    return zero,nonzero

############################################

def is_consistent_dumb(state,start_state,source):
    for i in range(state.shape[0]):
        for j in range(state.shape[1]):
            cur = state[i,j]
            zero,nonzero = find_neighbor(state,[i,j])
            color,count = np.unique(nonzero,return_counts=True)
            num = len(zero)+len(nonzero)

            # check assigned variable
            if cur != 0:
                if(len(zero)==0) and (cur not in color):
                        return False
                # check path zig-zag
                if start_state[i,j] == 0:
                    if count[color==cur] > 2:
                        return False
                # check source zig-zag
                else:
                    if count[color==cur] > 1:
                        return False
            # check unassigned variable            
            else:
                if(len(zero)==0):
                    if(len(color)==num):
                        return False
                    temp = color[count>2]
                    if len(temp) > 0:
                        return False
    return True


def is_complete_dumb(state,start_state):
    '''
    0: not complete with incomplete assignment
    1: not complete with complete assignment
    2: complete
    '''
    # check unassigned variable
    if 0 in state:
        return 0
    # check color path
    for row in range(state.shape[0]):
        for col in range(state.shape[0]):
            neighbor = neighbour([row,col],state)
            color,count = np.unique(neighbor,return_counts=True)
            # check path
            if start_state[row,col] == 0:
                if count[color==state[row,col]] != 2:
                    return 1
            # check source
            else:
                if count[color==start_state[row,col]] != 1:
                    return 1
    return 2


def select_variable_dumb(state,value):
    variable = np.column_stack(np.where(state==0))
    output = []
    for var in variable:
        neighbor = neighbour(var,state)
        color,count = np.unique(neighbor,return_counts=True)
        if count[color==0] == len(neighbor):
            continue
        if 0 in color:
            # [i,j,color]
            color = color.tolist()
            color.remove(0)
            for i in value:
                if i not in color:
                    idx = random.randint(0,len(color)-1)
                    color.insert(idx,i)
        output.append([var[0],var[1],color])
    idx = random.randint(0,len(output)-1)
    return output[idx]

def select_value_dumb(state,var):
    return var[2]


def recursive_backtrack_dumb(state,start_state,source,value,visit):
    global bt_counter
    check = is_complete_dumb(state,start_state)
    if check==1 or check==2:
        return state,check
    # print(state)
    var = select_variable_dumb(state,value)
    # print(var)
    for val in select_value_dumb(state,var):
        # print("var",var,"val",val)
        state[var[0],var[1]] = val
        record = state.tostring()
        if record not in visit:
            visit.add(record)
        else:
            continue
        # print("in")
        # print(state)
        if is_consistent_dumb(state,start_state,source):
            result,status = recursive_backtrack_dumb(state,start_state,source,value,visit)
            bt_counter += 1
            if status==2:
                return result,2
        state[var[0],var[1]] = 0
    return None,4

################################
puzzle = read_puzzles("input77.txt")
start_state,source,value = build_Start_State(puzzle)
bt_counter = 0

source = sorted(source,key=lambda list:list[2])
visit = set()
state = copy.deepcopy(start_state)

print_puzzles(puzzle)
print("Start State")
print(state,'\n')
start_time = time.time()
solution,status = recursive_backtrack_dumb(state,start_state,source,value,visit)
print_solution(solution)
print("Time used:",time.time()-start_time)
print("Total iteration:",bt_counter)