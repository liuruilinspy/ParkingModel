import random

from functools import reduce

from simulation.node import Node


def load_graph(file):
    """
    Load the graph structure from 'spot_graph'
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
        parking_spots = set()
        if len(tabs) > 2:
            p_s = tabs[2].split(",")
            parking_spots = set(map(int, p_s))
        node.parking_spots = parking_spots
        nodeset[id] = node

    # set neighbors for all the nodes
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


def generate_map(perctge):
    """
    Generate a random map by perctage
    :param perctge: percentage of occupancy
    :return:
    """
    # 0: empty 1: taken
    random_spot = random.sample(range(179), int(179 * perctge))
    spots = [0] * 179
    for i in random_spot:
        spots[i] = 1
    return spots


def search_path(start, end):
    """
    Search by BFS for paths in all direction
    :param start:
    :param end:
    :return:
    """
    queue = [(start, [start])]
    all_path = []
    while queue:
        (node, path) = queue.pop(0)
        for neighbor in node.neighbors - set(path):
            if neighbor == end:
                all_path.append(path + [neighbor])
            else:
                queue.append((neighbor, path + [neighbor]))
    if len(all_path) == 0:
        raise Exception("No path from Node(" + str(start.id) + ") to Node(" + str(end.id) + ")")
    else:
        return all_path


def all_path(nodeset):
    all_pair = {}
    for k1, start in nodeset.items():
        for k2, end in nodeset.items():
            if k1 == k2:
                continue
            all_paths = search_path(start, end)
            key = pair_key(start, end)
            all_pair[key] = all_paths
    return all_pair


def pair_key(start, end):
    return str(start.id) + "_" + str(end.id)


def shortest_path(all_pair, start, end):
    if start == end:
        return []
    key = pair_key(start, end)
    return min(all_pair[key], key=lambda p: len(p))


def shortest_path_by_direction(all_pair, start, end, next_node):
    key = pair_key(start, end)
    if key not in all_pair:
        raise Exception("Wrong key " + key)
    all_paths = all_pair[key]
    tmp = [p for p in all_paths if p[1] == next_node and start not in p[1:]]
    return min(tmp, key=lambda p: len(p))


def search_by_depth(all_pair, start, depth, d_cost, nodeset):
    """
    Search all the nodes with limited search depth
    :param start:
    :param depth:
    :param d_cost:
    :param nodeset:
    :param all_pair:
    :return:
    """
    search_result = {}
    for neighbor in start.neighbors:
        one_direction = []
        for k, end in nodeset.items():
            if start == end:
                continue
            path = shortest_path_by_direction(all_pair, start, end, neighbor)
            if len(path) * d_cost < depth:
                one_direction.append(path)
        search_result[neighbor] = one_direction
    return search_result


def candidates_probability(knowledge, prev_path, candidate_paths, all_pair, exit_node, best_cost, d_cost, w_cost, u_cost, p_available):
    """
    Calculate the not available probability
    :param knowledge:
    :param prev_path:
    :param candidate_paths:
    :param all_pair:
    :param exit_node:
    :param best_cost:
    :param d_cost:
    :param w_cost:
    :param u_cost:
    :param p_available:
    :return:
    """
    time_pr = {}
    cost_map = {}
    for path in candidate_paths:
        candidate_node = path[-1]
        drive_path = path
        drive_cost = len(drive_path) * d_cost
        walk_cost = len(shortest_path(all_pair, candidate_node, exit_node)) * w_cost
        uturn_cost = u_cost if is_uturn(prev_path, drive_path) else 0
        cost = drive_cost + walk_cost + uturn_cost
        if cost not in cost_map:
            cost_map[cost] = []
        cost_map[cost].append(candidate_node)
        if cost < best_cost:
            # better cost
            if knowledge[candidate_node.id] > 0:
                # known node with available parking spots
                p_not_exist = 0
            elif knowledge[candidate_node.id] > -1:
                # known node without available parking spots
                p_not_exist = 1
            else:
                # unknown node
                p_not_exist = 1 - p_available
        else:
            # no better cost
            p_not_exist = 1

        if cost not in time_pr:
            time_pr[cost] = []

        time_pr[cost].append(p_not_exist)
    return time_pr, cost_map


def choice_expectation(knowledge, all_pair, choices, exit_node, prev_path, best_cost, d_cost, w_cost, u_cost, p_available):
    exp = {}
    for next_node, candidates in choices.items():
        time_pr_cdf = []
        time_pr, cost_map = candidates_probability(knowledge, prev_path, candidates, all_pair, exit_node, best_cost, d_cost, w_cost, u_cost, p_available)
        items = sorted(time_pr.items(), key=lambda i: i[0])
        for time, p_list in items:
            p = reduce(lambda x, y: x * y, p_list)
            p_less_time = (1 - time_pr_cdf[-1][1]) if len(time_pr_cdf) > 0 else 1
            time_pr_cdf.append((time, 1 - (p * p_less_time)))
        t = [time_pr_cdf[0]] + [(y[0], y[1] - x[1]) for x, y in zip(time_pr_cdf, time_pr_cdf[1:])]
        e = sum(list(x*y for x, y in t))
        exp[next_node] = e
    return exp


def gain_knowledge(knowledge, node, spot_map):
    knowledge[node.id] = len(node.empty_parking_slot(spot_map))


def update_best_node(knowledge, all_pair, prev_path, nodeset, cur_node, exit_node, d_cost, w_cost, u_cost):
    """
    Recompute the best node and cost after every movement
    :param knowledge:
    :param prev_path:
    :param nodeset:
    :param cur_node:
    :param exit_node:
    :param d_cost:
    :param w_cost:
    :return:
    """
    best_cost = 10000000
    best_node = Node(-1)
    for i in range(len(knowledge)):
        if knowledge[i] > 0:
            walk_cost = len(shortest_path(all_pair, nodeset[i], exit_node)) * w_cost
            drive_path = shortest_path(all_pair, cur_node, nodeset[i])
            drive_cost = len(drive_path) * d_cost
            uturn_cost = u_cost if is_uturn(prev_path, drive_path) else 0
            cost = drive_cost + walk_cost + uturn_cost
            if cost < best_cost:
                best_cost = cost
                best_node = nodeset[i]
    return best_cost, best_node


def is_uturn(prev_path, to_path):
    if len(prev_path) > 1 and len(to_path) > 1 and prev_path[-2] == to_path[1]:
        return True
    return False


def all_node_visited(nodeset, knowledge):
    """
    Test if all the node is visited
    :param nodeset:
    :param knowledge:
    :return:
    """
    for key, val in nodeset.items():
        if knowledge[val.id] < 0:
            return False
    return True


def node_list_deep_copy(node_list):
    new_list = []
    for node in node_list:
        new_list.append(node.copy())
    return new_list


def execute(spot_map, nodeset, all_pair, knowledge, enter_node, exit_node, p_available, d_cost, w_cost, default_best_cost, saving_threshold):

    cur_node = enter_node
    best_cost = default_best_cost
    best_node = Node(-1)
    prev_path = [enter_node]

    finished = False

    gain_knowledge(knowledge, cur_node, spot_map)

    while not finished:
        # print(cur_node)
        if cur_node.id == 241:
            x=0
        choices = search_by_depth(all_pair, cur_node, best_cost, d_cost, nodeset)
        exp = choice_expectation(knowledge, all_pair, choices, exit_node, prev_path, best_cost, d_cost, w_cost, u_cost, p_available)
        next_node, best_saving = max(exp.items(), key=lambda e: best_cost - e[1])
        if best_saving < saving_threshold:
            path = shortest_path(all_pair, cur_node, best_node)
            cur_node = path[1]

        else:
            cur_node = next_node

        gain_knowledge(knowledge, cur_node, spot_map)
        prev_path.append(cur_node)
        best_cost, best_node = update_best_node(knowledge, all_pair, prev_path, nodeset, cur_node, exit_node, d_cost, w_cost, u_cost)

        if all_node_visited(nodeset, knowledge):
            finished = True

        if len(prev_path) > 200:
            print(str(prev_path[-1]), str(prev_path[-2]))
            raise Exception("Fall into infinite loop")
    return best_node, prev_path


if __name__ == "__main__":

    nodeset = load_graph("spot_graph")

    enter_node = nodeset[219]
    exit_node = nodeset[253]
    p_available = 0.5

    d_cost = 1
    w_cost = 4
    u_cost = 8


    all_pair = all_path(nodeset)
    spot_map = [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1]

    # for i in range(10):
    # spot_map = generate_map(0.7)
    print(spot_map)
    knowledge = [-1] * 291
    # used as threshold when entering the parking lot
    default_best_cost = 10000
    saving_threshold = 10
    best_node, prev_path = execute(spot_map, nodeset, all_pair, knowledge, enter_node, exit_node, p_available, d_cost, w_cost, default_best_cost, saving_threshold)
    print(best_node, len(prev_path), list(map(lambda n: n.id, prev_path)))

