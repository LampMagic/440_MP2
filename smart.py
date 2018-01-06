
import numpy as np
import time
from copy import deepcopy


'''
@ function: read in raw puzzle
@ param:    txt file path
@ return:   array of raw puzzle
'''
def read_puzzles(textPuzzles):
    file = open(textPuzzles,'r')
    text = file.read()
    line = text.splitlines()
    return np.asarray([list(x) for x in line])


'''
@ function: print out raw puzzle
@ param:    array of raw puzzle
@ return:   none
'''
def print_puzzles(puzzles):
    print("\nPrinting raw puzzle")
    print("rc0123456789")
    i = 0
    for line in puzzles:
        print(i,''.join(line))
        i += 1
    print("\n")


'''
@ function: print out solution
@ param:    matrix of solution
@ return:   none
'''
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

 
'''
@ function: build up start state for backtacking
@ param:    array of raw puzzle
@ return:   output: Matrix of puzzle with character stored as number
            source: Array of color sources with each entry storing [i,j,color]
            value: Array of color value in puzzle
'''    
def build_Start_State(rawPuzzle):
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


'''
@ function: find neighbors of a given poistion
@ param:    location: query position index
            state: current state
@ return:   output: Array of neighbor color value
''' 
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


'''
@ function: find neighbors of a given position
@ param:    state: current state
            cur: query position index
@ return:   zero: Array of unassigned neighbor index
            nonzero: Array of assigned neighbor color
''' 
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


'''
@ function: check state consistency w.r.t constraints
@ param:    state: current state
            start_state: initial state
            source: Array of color source
@ return:   boolean value of current consistency        
''' 
def is_consistent(state,start_state,source):
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
    # forward checking                  
    return checkLink(state,source)


'''
@ function: check state completeness w.r.t constraints
@ param:    state: current state
            start_state: initial state
@ return:   boolean value of current completeness
''' 
def is_complete(state,start_state):
    # check for unassigned variable
    if 0 in state:
        return False
    # check color path
    for row in range(state.shape[0]):
        for col in range(state.shape[0]):
            neighbor = neighbour([row,col],state)
            color,count = np.unique(neighbor,return_counts=True)
            # check path
            if start_state[row,col] == 0:
                if count[color==state[row,col]] != 2:
                    return False
            # check source
            else:
                if count[color==start_state[row,col]] != 1:
                    return False
    return True


'''
@ function: select variable for assignment
@ param:    state: current state
            value: Array of all color value
            connected: Array of value that should not be used
@ return:   variable with most assignable value
''' 
def select_variable(state,value,connected):
    variable = np.column_stack(np.where(state==0))
    output = []
    for var in variable:
        neighbor = neighbour(var,state)
        color,count = np.unique(neighbor,return_counts=True)
        if count[color==0] == len(neighbor):
            continue
        color = [x for _,x in sorted(zip(count.tolist(),color.tolist()),reverse=True)]
        if 0 in color:
            # [i,j,color]
            color.remove(0)
            for i in value:
                if i not in color:
                    color.append(i)

        for i in connected:
            if i in color:
                color.remove(i)
        output.append([var[0],var[1],color])

    output = sorted(output,key=lambda list:len(list[2]))
    return output[0]


'''
@ function: find assignable value given a variable
@ param:    var: current variable
@ return:   Array of assignable value
''' 
def select_value(var):
    return var[2]


'''
@ function: recursive backtracking to find solution
@ param:    state: current state
            start_state: initial state
            source: Array of color source
            value: Array of all color value
            visit: Set of visited state
@ return:   Array of assignable value
''' 
def recursive_backtrack(state,start_state,source,value,visit):
    global bt_counter
    if is_complete(state,start_state):
        return state
    connected = checkColor(state,source)
    var = select_variable(state,value,connected)

    for val in select_value(var):
        state[var[0],var[1]] = val
        record = state.tostring()
        if record not in visit:
            visit.add(record)
        else:
            continue

        if is_consistent(state,start_state,source):
            result = recursive_backtrack(state,start_state,source,value,visit)
            bt_counter += 1
            if result is not None:
                return result
        state[var[0],var[1]] = 0

    return None


'''
@ function: find forced move in initial state and go for it
@ param:    state: initial state
            source: Array of color source
@ return:   updated initial state without forced move
''' 
def forced_move(state,source):
    forced = []
    for src in source:
        zero,nonzero = find_neighbor(state,[src[0],src[1]])
        color,count = np.unique(nonzero,return_counts=True)
        if (len(zero)==1):
            if(src[2] in color) and (count[src[2]==color]>1):
                continue
            state[zero[0][0],zero[0][1]] = src[2]
            forced.append(zero[0])

    return forced_iter(state,forced)


'''
@ function: helper function that eliminates forced move
@ param:    state: initial state
            forced: Array of forced move
@ return:   updated initial state without forced move
''' 
def forced_iter(state,forced):
    while len(forced) != 0:
        for force in forced:
            forced.remove(force)
            zero,nonzero = find_neighbor(state,[force[0],force[1]])
            color,count = np.unique(nonzero,return_counts=True)

            if (len(zero)==1):
                if(state[force[0],force[1]] in color) and (count[state[force[0],force[1]]==color]>1):
                    continue
                state[zero[0][0],zero[0][1]] = state[force[0],force[1]]
                forced.append(zero[0])

    return state


'''
@ function: forward checking helper function
@ param:    state: current state
            source: Array of color source
@ return:   boolean value of forward checking consistency
'''
def checkLink(state,source):
    for i in range(0,len(source),2):
        start = [source[i][0],source[i][1]]
        goal = [source[i+1][0],source[i+1][1]]
        # use BFS to check linkage
        if not BFS(state,start,goal):
            return False

    return True


'''
@ function: helper function that checks completed color value
@ param:    state: current state
            source: Array of color source
@ return:   Array of color value that is completed hence should not be used anymore
'''
def checkColor(state,source):
    connected = []
    for i in range(0,len(source),2):
        start = [source[i][0],source[i][1]]
        goal = [source[i+1][0],source[i+1][1]]
        # use BFS to check connection
        if BFScolor(state,start,goal):
            connected.append(source[i][2])

    return connected


'''
@ function: helper function for BFS that find neighbor given position
@ param:    location: query position index
            puzzles: current state
@ return:   output: Array of neighbor index
'''
def bfs_neighbor(location,puzzles):
    output = []
    if location[0]>0:
        output.append([location[0]-1,location[1]])

    if location[0]<puzzles.shape[1]-1:
        output.append([location[0]+1,location[1]])

    if location[1]>0:
        output.append([location[0],location[1]-1])

    if location[1]<puzzles.shape[0]-1:
        output.append([location[0],location[1]+1])

    return output


'''
@ function: Breadth First Search that check if two color sources can be connected
@ param:    state: current state
            start: start position of search
            goal: goal position of search
@ return:   boolean value of current connectability
'''
def BFS(state,start,goal):
    front_list = [start]
    visit_list = []
    goal_color = state[goal[0],goal[1]]
    flag = False

    while(len(front_list)):
        frontier = front_list.pop(0)
        if frontier == goal:
            return True

        if frontier not in visit_list:
            visit_list.append(frontier)
            children = bfs_neighbor(frontier,state)
            zero,nonzero = find_neighbor(state,frontier)

            if goal_color in nonzero:
                flag = True
            else:
                flag = False

            for child in children:
                if (child not in front_list) and (child not in visit_list):
                    if flag and (state[child[0],child[1]] == goal_color):
                        front_list.append(child)
                    elif (state[child[0],child[1]] == 0):
                        front_list.append(child)
    return False


'''
@ function: Breadth First Search that check if two color sources are connected
@ param:    state: current state
            start: start position of search
            goal: goal position of search
@ return:   boolean value of current connection status
'''
def BFScolor(state,start,goal):
    front_list = [start]
    visit_list = []
    goal_color = state[goal[0],goal[1]]
    flag = False

    while(len(front_list)):
        frontier = front_list.pop(0)
        if frontier == goal:
            return True

        if frontier not in visit_list:
            visit_list.append(frontier)
            children = bfs_neighbor(frontier,state)

            for child in children:
                if (child not in front_list) and (child not in visit_list):
                    if (state[child[0],child[1]] == goal_color):
                        front_list.append(child)
    return False

###########################################################################

puzzle = read_puzzles("input991.txt")
start_state,source,value = build_Start_State(puzzle)
source = sorted(source,key=lambda list:list[2])
visit = set()
state = deepcopy(start_state)

print_puzzles(puzzle)
print("Start State")
print(state,'\n')

bt_counter = 0
start_time = time.time()
state = forced_move(state,source)
print("Forced State")
print(state,'\n')

solution = recursive_backtrack(state,start_state,source,value,visit)
print("Goal State")
print(solution,'\n')
print("Time used:",time.time()-start_time)
print("Total iteration:",bt_counter)