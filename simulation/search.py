import random
from operator import itemgetter

from simulation.node import Node


def generate_map(perctge):
    """
    Generate a random map by perctage
    :param perctge: percentage of occupancy
    :return:
    """
    # 0: empty 1: taken
    random_slot = random.sample(range(179), int(178 * perctge))
    slots = [0] * 179
    for i in random_slot:
        slots[i] = 1
    return slots


def load_graph(file):
    """
    Load the graph structure from 'spot_graph'
    402, 403, 404 are fake nodes for easy searching

    217-402-219-404-254
             |
            403
             |
             220
    :param file: spot_graph
    :return:
    """
    nodeset = {}
    lines = [line.rstrip("\n") for line in open(file, "r")]

    # initialize all the nodes
    for line in lines:
        tabs = line.split(" ")
        id = int(tabs[0])
        node = Node(id)
        if len(tabs) > 2:
            p_s = tabs[2].split(",")
            parking_slots = set(map(int, p_s))
            node.parking_slots = parking_slots
        nodeset[id] = node

    # set neigbors for all the nodes
    for line in lines:
        tabs = line.split(" ")
        n_i = tabs[1].split(",")
        neighbors_id = set(map(int, n_i))
        neighbors = []
        for n in neighbors_id:
            neighbors.append(nodeset[n])
        id = int(tabs[0])
        nodeset[id].neighbors = set(neighbors)

    return nodeset


def search_by_end(begin, end, visited):
    stack = [(begin, [begin])]
    paths = []
    while stack:
        (node, path) = stack.pop()
        for neighbor in node.neighbors - set(path) - visited:
            if neighbor == end:
                paths.append(path + [neighbor])
            else:
                stack.append((neighbor, path + [neighbor]))
    return paths


def search_by_depth(slot_map, begin, exit_slot, p, significance, cost_depth, d_cost, w_cost, u_cost, visited, drive_path):
    stack = [(begin, [begin])]
    paths = []
    while stack:
        (node, path) = stack.pop()
        for neighbor in node.neighbors - set(path) - visited:
            ipath = path + [neighbor]
            exp = path_exp(ipath, 0, drive_path, p, significance, exit_slot, d_cost, w_cost, u_cost, slot_map)
            # walk_cost = walk(neighbor, exit_slot, w_cost)
            # drive_cost = len(path) * d_cost
            # print(path[-1].id, walk_cost, drive_cost)
            if exp < cost_depth:
                # if len(neighbor.empty_parking_slot(slot_map)) == 0:
                #     next_path = find_next_available(drive_path[:-1]+path, slot_map)
                #     path = path[:-1] + next_path
                paths.append(ipath)
            else:
                stack.append((neighbor, ipath))
    return paths

def uturn_exp(drive_path, cur_slot, exit_slot, slot_map, d_cost, w_cost, u_cost, default_cost = 90):
    min_node, min_cost = Node(-1), 1000000000
    for slot in drive_path:
        if len(slot.empty_parking_slot(slot_map)) > 0:
            path = min(search_by_end(cur_slot, slot, set()), key=lambda p : len(p))
            cost = len(path) * d_cost + walk(cur_slot, exit_slot, w_cost) + u_cost
            if cost < min_cost:
                min_node = slot
                min_cost = cost
    if min_node.id == -1:
        return default_cost
    return min_cost


def merge_path(paths):
    """
    Merge the repeated beginning parts of two path

    :return:
    """
    if len(paths) <= 1:
        return paths

    min_len = len(min(paths, key=lambda p: len(p)))
    common = []
    flag = True
    for i in range(min_len):
        co = paths[0][i]
        for p in paths:
            if p[i] != co:
                flag = False
        if flag:
            common.append(co)
        else:
            break

    return_val = [common]
    for p in paths:
        return_val.append([x for x in p if x not in common])
    return return_val


def path_exp(path, drived_step, drive_path, p, significance, exit_slot, d_cost, w_cost, u_cost, slot_map, default_cost=90):

    cur_slot = path[0]
    has_parking_slots = len(cur_slot.empty_parking_slot(slot_map)) > 0
    walk_cost = walk(path[0], exit_slot, w_cost)
    drive_cost = drived_step * d_cost

    if len(path) == 1:
        if has_parking_slots:
            return (1 - significance) * (drive_cost + walk_cost)
        else:
            return (1 + significance) * uturn_exp(drive_path, cur_slot, exit_slot, slot_map, d_cost, w_cost, u_cost)
    else:
        if has_parking_slots:
            return (p - significance) * (drive_cost + walk_cost) + \
                   (1 - p + significance) * (drive_cost + path_exp(path[1:], drived_step+1, drive_path, p, significance, exit_slot, d_cost, w_cost, u_cost, slot_map))
        else:
            return (1 + significance) * path_exp(path[1:], drived_step+1, drive_path, p, significance, exit_slot, d_cost, w_cost, u_cost, slot_map)


def walk(cur_slot, exit_slot, w_cost):
    # min length from current node to exit slot
    all_paths = search_by_end(cur_slot, exit_slot, set())
    if len(all_paths) == 0:
        # arrive at the exit slot
        return 0
    p_exit = min(all_paths, key=lambda p: len(p))
    return len(p_exit) * w_cost


def start(slot_map, enter_slot, exit_slot, nodeset, default_depth, p=0.5, significance=0.05, d_cost=1, w_cost=3, u_cost=10):

    stop = False
    cur_slot = enter_slot
    knowledge = [-1] * 179
    drive_path = []
    while not stop:
        # gain knowledge of visited slot
        gain_knowledge(knowledge, cur_slot, slot_map)
        drive_path.append(cur_slot)
        # DFS search paths within the cost depth
        cost_depth = get_cost_depth(slot_map, cur_slot, exit_slot, d_cost, w_cost, drive_path, default_depth)
        all_paths = search_by_depth(slot_map, cur_slot, exit_slot, p, significance, cost_depth, d_cost, w_cost, u_cost, set(), drive_path)

        path, exp_cost = best_path(all_paths, drive_path, p, significance, exit_slot, d_cost, w_cost, u_cost, slot_map)
        if len(cur_slot.empty_parking_slot(slot_map)) == 0:
            cur_slot = path[1]
        else:
            walk_cost = walk(cur_slot, exit_slot, w_cost)
            if walk_cost <= exp_cost:
                stop = True
                # print("walk_cost", walk_cost)
                # print("exp_cost", exp_cost)
                return drive_path, len(drive_path) * d_cost + walk_cost
            else:
                cur_slot = path[1]

        if knowledge_completed(knowledge):
            print("glable_optimum")
            return globe_optimum(slot_map, enter_slot, exit_slot, nodeset, d_cost, w_cost)


def globe_optimum(slot_map, enter_slot, exit_slot, nodeset, d_cost, w_cost):
    # find globe optimum when all the slots are visited
    min_index, min_exp = -1, 1000000000
    for slot in range(180, 290):
        cur_slot = nodeset[slot]
        if len(cur_slot.empty_parking_slot(slot_map)) > 0:
            drive_path = shortest_path(search_by_end(enter_slot, cur_slot, set()))
            walk_path = shortest_path(search_by_end(cur_slot, exit_slot, set()))
            exp = d_cost * len(drive_path) + w_cost * len(walk_path)
            if exp < min_exp:
                min_index, min_exp = slot, exp
    return min_index, min_exp


def get_cost_depth(slot_map, cur_slot, exit_slot, d_cost, w_cost, drive_path, default_depth):
    # get the search depth in different situations
    if len(cur_slot.empty_parking_slot(slot_map)) == 0:
        for i in reversed(range(len(drive_path))):
            if len(drive_path[i].empty_parking_slot(slot_map)) > 0:
                return walk(drive_path[i], exit_slot, w_cost)
        return default_depth
    else:
        return walk(cur_slot, exit_slot, w_cost)


def best_path(all_paths, drive_path, p, significance, exit_slot, d_cost, w_cost, u_cost, slot_map):
    # select the path with min cost expectation
    exps = []
    for path in all_paths:
        exp = path_exp(path, 0, drive_path, p, significance, exit_slot, d_cost, w_cost, slot_map)
        if is_uturn(drive_path, path):
            exp += u_cost
        exps.append(exp)
    index, exp_cost = min(enumerate(exps), key=itemgetter(1))
    return all_paths[index], exp_cost


def shortest_path(all_paths):
    # select the path with min length
    if len(all_paths) > 0:
        return min(all_paths, key= lambda p: len(p))
    return None


def gain_knowledge(knowledge, cur_slot, slot_map):
    if hasattr(cur_slot, "parking_slots"):
        for slot in cur_slot.parking_slots:
            knowledge[slot] = slot_map[slot]


def knowledge_completed(knowledge):
    for k in knowledge:
        if k == -1:
            return False
    return True

def is_uturn(path_a, path_b):
    if len(path_a) < 2 or len(path_b) < 2:
        return False
    elif path_a[-2] == path_b[1]:
        return True
    else:
        return False

def save_result(file_path, result):
    fo = open(file_path, "a")
    for cost, drive_path, slot_map in result:
        path_str = []
        for node in drive_path:
            path_str.append(node.id)
        s = str(cost) + "\t" + str(drive_path[-1].id) + "\t" + str(path_str) + "\t" + str(slot_map) + "\n"
        fo.write(s)
    fo.close()


if __name__ == "__main__":

    nodeset = load_graph("spot_graph")
    slot_map = generate_map(0.5)

    significance = 0.05
    # assumed parking probability
    pr = 0.5
    # unit drive cost
    d_cost = 1
    # unit walk cost
    w_cost = 3
    # unit u turn cost
    u_cost = 10
    enter_slot = nodeset[219]
    exit_slot = nodeset[253]
    default_depth = 90
    drive_path, cost = start(slot_map, enter_slot, exit_slot, nodeset, default_depth, pr, significance, d_cost, w_cost, u_cost)
    print(len(drive_path), cost)

    # result = []
    # for i in range(100):
    #     slot_map = generate_map(0.5)
    #     drive_path, cost = start(slot_map, enter_slot, exit_slot, nodeset, default_depth, pr, significance, d_cost, w_cost, u_cost)
    #     print(len(drive_path), cost)
    #     r = [cost, drive_path, slot_map]
    #     result.append(r)
    # save_result("result", result)

    # print(path_exp([nodeset[219], nodeset[220], nodeset[221]], 0, [nodeset[219], nodeset[220]], pr, significance, exit_slot, d_cost, w_cost, u_cost, slot_map))

