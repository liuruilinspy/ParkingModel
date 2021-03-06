import random

from functools import reduce

import scipy.stats

from simulation.node import Node


def load_spot_graph(file):
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
        node = Node(id, "D")
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


def generate_map(perctge, total_spots):
    """
    Generate a random map by perctage
    :param perctge: percentage of occupancy
    :return:
    """
    # 0: empty 1: taken
    random_spot = random.sample(range(total_spots), int(round(total_spots * perctge)))
    spots = [0] * total_spots
    for i in random_spot:
        spots[i] = 1
    return spots


def generate_gaussian_map(all_pair, exit_node, sigma, perctge, total_spots):
    spot_map = [0] * total_spots
    occupancy = int(total_spots * perctge)

    distance_distribution = {}

    # node list in every distance
    for key, node in nodeset.items():
        if node == exit_node:
            continue
        p = shortest_path(all_pair, exit_node, node)
        if len(p) not in distance_distribution:
            distance_distribution[len(p)] = []
        distance_distribution[len(p)].append(node)

    exp = 0
    pdf = {}
    slots = {}
    for key, val in distance_distribution.items():
        p = round(scipy.stats.norm(0, sigma).pdf(key / 3), 2)
        pdf[key] = p
        parking = set()
        for slot in val:
            parking.update(slot.empty_parking_slot(spot_map))
        slots[key] = parking
        exp += len(parking) * p

    # increment to comply with total occupancy percentage
    increment = (occupancy - exp) / total_spots

    print(increment)

    random_spot = []
    for key, val in distance_distribution.items():
        # print(key,len(slots[key]), pdf[key] + increment)
        n = int(round(len(slots[key]) * pdf[key]) + round(len(slots[key]) * increment))
        s = n if n <= len(slots[key]) else len(slots[key])
        random_spot += random.sample(slots[key], s)

    print(len(random_spot) / total_spots, len(random_spot) - occupancy)
    for s in random_spot:
        spot_map[s] = 1

    return spot_map


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
    best_cost = 250
    # dummy best node
    best_node = Node(-1, "D")
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
    # get if the next direction requires u turn
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


def total_cost(path, all_pair, exit_node, d_cost, w_cost, u_cost):
    cost = 0
    i = -2
    for j in range(len(path)):
        cost += d_cost
        if i >= 0 and path[i] == path[j]:
            cost += u_cost
        i += 1
    cost += w_cost * len(shortest_path(all_pair, path[-1], exit_node))
    return cost


def execute(spot_map, nodeset, all_pair, knowledge, enter_node, exit_node, p_available, x, d_cost, w_cost, u_cost, default_best_cost, saving_threshold):

    cur_node = enter_node
    best_cost = default_best_cost
    # dummy best node
    best_node = Node(-1, "D")
    prev_path = [enter_node]

    finished = False

    gain_knowledge(knowledge, cur_node, spot_map)

    back_steps = 0

    while not finished:
        # possible candidates of each direction
        choices = search_by_depth(all_pair, cur_node, best_cost, d_cost, nodeset)
        # saving time expectation of each direction
        exp = choice_expectation(knowledge, spot_map, all_pair, choices, exit_node, prev_path, best_cost, d_cost, w_cost, u_cost, p_available, x)
        # best expected saving time
        next_node, best_saving = max(exp.items(), key=lambda t_e: t_e[1])
        if best_saving < saving_threshold:
            if cur_node == best_node:
                # arrive at best spot
                finished = True
            else:
                # head to current best spot
                path = shortest_path(all_pair, cur_node, best_node)
                cur_node = path[1]
                back_steps += 1
        else:
            cur_node = next_node

        gain_knowledge(knowledge, cur_node, spot_map)
        prev_path.append(cur_node)
        best_cost, best_node = update_best_node(knowledge, all_pair, prev_path, nodeset, cur_node, exit_node, d_cost, w_cost, u_cost)

        if all_node_visited(nodeset, knowledge):
            finished = True

        if len(prev_path) > 200:
            print(str(prev_path[-1]), str(prev_path[-2]), str(prev_path[-3]))
            raise Exception("Fall into infinite loop")
    return best_node, prev_path, back_steps


def candidates_probability(knowledge, spot_map, prev_path, candidate_paths, all_pair, exit_node, best_cost, d_cost, w_cost, u_cost, p_available, x):
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
                if len(candidate_node.empty_parking_slot(spot_map)) > 0:
                    p_not_exist += x
                else:
                    p_not_exist -= x
        else:
            # no better cost
            p_not_exist = 1

        if cost not in time_pr:
            time_pr[cost] = []

        time_pr[cost].append(p_not_exist)
    return time_pr, cost_map


def choice_expectation(knowledge, spot_map, all_pair, choices, exit_node, prev_path, best_cost, d_cost, w_cost, u_cost, p_available, x):
    exp = {}
    for next_node, candidates in choices.items():
        saving_time_pr_cdf = []
        time_pr, cost_map = candidates_probability(knowledge, spot_map, prev_path, candidates, all_pair, exit_node, best_cost, d_cost, w_cost, u_cost, p_available, x)
        items = sorted(time_pr.items(), key=lambda i: i[0])
        e = 0
        for time, p_list in items:
            p_equal_to_time = reduce(lambda x, y: x * y, p_list)
            p_less_than_time = (1 - saving_time_pr_cdf[-1][1]) if len(saving_time_pr_cdf) > 0 else 1
            # saving_time = best_cost - time
            saving_time_pr_cdf.append((best_cost - time, 1 - (p_equal_to_time * p_less_than_time)))
        t = [saving_time_pr_cdf[0]] + [(y[0], y[1] - x[1]) for x, y in zip(saving_time_pr_cdf, saving_time_pr_cdf[1:])]
        exp[next_node] = sum(list(x*y for x, y in t))
    return exp


if __name__ == "__main__":

    nodeset = load_spot_graph("spot_graph")

    enter_node = nodeset[219]
    exit_node = nodeset[253]
    p_available = 0.5

    x = 0.2

    # drive cost of one spot distance
    d_cost = 1
    # walk cost of one spot distance
    w_cost = 4
    # u turn cost of one spot distance
    u_cost = 8


    all_pair = all_path(nodeset)

    # simple test

    total_spots = 179
    # occupancy density
    density = 10
    # stop forward search threshold
    saving_threshold = 10
    # visited node
    knowledge = [-1] * 291
    # used as threshold when entering the parking lot
    default_best_cost = 250

    sigma = 1

    # spot_map = generate_gaussian_map(nodeset, exit_node, sigma, density / 100, total_spots)
    #
    # best_node, path, back_steps = execute(spot_map, nodeset, all_pair, knowledge, enter_node, exit_node,
    #                                            p_available, x, d_cost, w_cost, u_cost, default_best_cost, saving_threshold)
    # print("Final:", path[-1], "ParkOption:", path[-1].empty_parking_slot(spot_map), "Length:", len(path),
    #       "BackSteps:", back_steps, "Cost:", total_cost(path, all_pair, exit_node, d_cost, w_cost, u_cost))

    fo = open("result_sample.txt", "w")
    fo.write(
        "density \t saving_threshold \t x_value \t final_position \t path_length \t cost \t back_steps \t final_parking_options \t path \t map \n")
    for saving_threshold in [10, 20, 30, 40]:
        for density in range(10, 100, 10):
            for x in [0, 0.1, 0.2, 0.3]:
                print("Setting: ", saving_threshold, density, x)
                for i in range(1):
                    # spot_map = generate_map(density / 100)
                    spot_map = generate_gaussian_map(all_pair, exit_node, sigma, density / 100, total_spots)
                    knowledge = [-1] * 291
                    # used as threshold when entering the parking lot
                    default_best_cost = 250
                    best_node, prev_path, back_steps = execute(spot_map, nodeset, all_pair, knowledge, enter_node,
                                                               exit_node,
                                                               p_available, x, d_cost, w_cost, u_cost,
                                                               default_best_cost, saving_threshold)
                    cost = total_cost(prev_path, all_pair, exit_node, d_cost, w_cost, u_cost)
                    print("Final:", prev_path[-1], "ParkOption:", prev_path[-1].empty_parking_slot(spot_map), "Length:",
                          len(prev_path), "BackSteps:", back_steps, "Cost: ", cost)
                    # density, saving_threshold, final position, path length, back steps, final parking options, path, map
                    fo.write(str(density) + "\t" + str(saving_threshold) + "\t" + str(x) + "\t"
                             + str(prev_path[-1]) + "\t" + str(len(prev_path)) + "\t" + str(cost)
                             + "\t" + str(back_steps) + "\t" + str(prev_path[-1].empty_parking_slot(spot_map))
                             + "\t" + str(list(map(lambda n: n.id, prev_path))) + "\t" + str(spot_map) + "\n")
    fo.close()