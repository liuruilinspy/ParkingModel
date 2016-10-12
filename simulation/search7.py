import datetime
import random

from functools import reduce

import scipy.stats

from simulation.generate_graph import generate_graph
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


def generate_gaussian_map(nodeset, all_pair, exit_node, sigma, perctge, total_spots):
    spot_map = [0] * total_spots
    occupancy = int(total_spots * perctge)
    spot_pdf = {}

    distance_distribution = {}

    # node list in every distance
    nodeitems = [(key, val) for key, val in nodeset.items() if val.type == "D"]
    for key, node in nodeitems:
        p = shortest_path(all_pair, node, exit_node)[1:]
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
            parking.update(slot.empty_parking_spot(spot_map))
        slots[key] = parking
        exp += len(parking) * p


    # increment to comply with total occupancy percentage
    increment = (occupancy - exp) / total_spots

    # print(increment)

    random_spot = []
    for key, val in distance_distribution.items():
        # print(key,len(slots[key]), pdf[key] + increment)
        n = int(round(len(slots[key]) * pdf[key]) + round(len(slots[key]) * increment))
        s = n if n <= len(slots[key]) else len(slots[key])
        random_spot += random.sample(slots[key], s)
        for v in val:
            spot_pdf[v.id] = pdf[key] + increment

    # print(len(random_spot) / total_spots, len(random_spot) - occupancy)
    for s in random_spot:
        spot_map[s] = 1

    return spot_map, spot_pdf


def search_path(start, end):
    """
    Search by BFS for paths in all direction
    :param start:
    :param end:
    :return:
    """
    if start == end:
        return [[start]]
    all_path = []
    queue = [(start, [start])]
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
    for k1, start in nodeset:
        for k2, end in nodeset:
            all_paths = search_path(start, end)
            key = pair_key(start, end)
            all_pair[key] = all_paths
    return all_pair


def pair_key(start, end):
    return str(start.id) + "_" + str(end.id)


def shortest_path(all_pair, start, end):
    if start == end:
        return [start]
    key = pair_key(start, end)
    if len(all_pair[key]) == 0:
        return []
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
            if start == end or end.type != "D":
                continue
            path = shortest_path_by_direction(all_pair, start, end, neighbor)[1:]
            if len(path) * d_cost < depth:
                one_direction.append(path)
        search_result[neighbor] = one_direction
    return search_result


def gain_knowledge(knowledge, node, spot_map):
    knowledge[node.id] = len(node.empty_parking_spot(spot_map))


def update_best_node(knowledge, all_pair, prev_path, nodeset, cur_node, exit_node, best_cost, best_node, d_cost, w_cost, u_cost):
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
    for i in range(len(knowledge)):
        if knowledge[i] > 0:
            walk_cost = (len(shortest_path(all_pair, nodeset[i], exit_node)) - 1) * w_cost
            drive_path = shortest_path(all_pair, cur_node, nodeset[i])[1:]
            drive_cost = len(drive_path) * d_cost
            uturn_cost = u_cost if is_uturn(prev_path, drive_path) else 0
            cost = drive_cost + walk_cost + uturn_cost
            if cost < best_cost:
                best_cost = cost
                best_node = nodeset[i]
    return best_cost, best_node


def is_uturn(prev_path, to_path):
    # get if the next direction requires u turn
    if len(prev_path) > 1 and len(to_path) > 0 and prev_path[-2] == to_path[0]:
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



def candidates_probability(knowledge, spot_map, prev_path, candidate_paths, all_pair, exit_node, best_cost, d_cost, w_cost, u_cost, x):
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
    :return:
    """
    time_pr = {}
    cost_map = {}
    for path in candidate_paths:
        candidate_node = path[-1]
        drive_path = path
        drive_cost = len(drive_path) * d_cost
        walk_cost = (len(shortest_path(all_pair, candidate_node, exit_node)) - 1) * w_cost
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
                p_not_exist = unknown_probability(candidate_node, x, candidate_node.empty_parking_spot(spot_map))
        else:
            # no better cost
            p_not_exist = 1

        if cost not in time_pr:
            time_pr[cost] = []

        time_pr[cost].append(p_not_exist)
    return time_pr, cost_map


def unknown_probability(candidate_node, x, parking_spot):
    if x == "G":
        return 0 if len(parking_spot) > 0 else 1
    elif isinstance(x, float):
        return x if len(parking_spot) > 0 else 1 - x
    elif isinstance(x, dict):
        return 1 - x[candidate_node.id]
    else:
        raise Exception("Wrong type x")


def choice_expectation(knowledge, spot_map, all_pair, choices, exit_node, prev_path, best_cost, d_cost, w_cost, u_cost, x):
    exp = {}
    for next_node, candidates in choices.items():
        saving_time_pr_cdf = []
        time_pr, cost_map = candidates_probability(knowledge, spot_map, prev_path, candidates, all_pair, exit_node, best_cost, d_cost, w_cost, u_cost, x)
        items = sorted(time_pr.items(), key=lambda i: i[0])
        for time, p_list in items:
            p_equal_to_time = reduce(lambda x, y: x * y, p_list)
            p_less_than_time = (1 - saving_time_pr_cdf[-1][1]) if len(saving_time_pr_cdf) > 0 else 1
            # saving_time = best_cost - time
            saving_time_pr_cdf.append((best_cost - time, 1 - (p_equal_to_time * p_less_than_time)))
        t = [saving_time_pr_cdf[0]] + [(y[0], y[1] - x[1]) for x, y in zip(saving_time_pr_cdf, saving_time_pr_cdf[1:])]
        exp[next_node] = sum(list(x*y for x, y in t))
    return exp


def execute(spot_map, nodeset, all_pair, knowledge, enter_node, exit_node, x, d_cost, w_cost, u_cost, default_best_cost, saving_threshold):

    cur_node = enter_node
    best_cost = default_best_cost
    # dummy best node
    best_node = Node(0, "D")
    prev_path = [enter_node]

    finished = False

    gain_knowledge(knowledge, cur_node, spot_map)

    back_steps = 0

    while not finished:
        # possible candidates of each direction
        choices = search_by_depth(all_pair, cur_node, best_cost, d_cost, nodeset)
        # saving time expectation of each direction
        exp = choice_expectation(knowledge, spot_map, all_pair, choices, exit_node, prev_path, best_cost, d_cost, w_cost, u_cost, x)
        # best expected saving time
        next_node, best_saving = max(exp.items(), key=lambda t_e: t_e[1])
        if best_saving < saving_threshold:
            if cur_node == best_node:
                # arrive at best spot
                finished = True
            else:
                # head to current best spot
                path = shortest_path(all_pair, cur_node, best_node)
                if len(path) == 1 or len(path) == 0:
                    print(saving_threshold, x, cur_node.id, best_node.id, exp)
                cur_node = path[1]
                back_steps += 1
        else:
            cur_node = next_node

        gain_knowledge(knowledge, cur_node, spot_map)
        prev_path.append(cur_node)
        best_cost, best_node = update_best_node(knowledge, all_pair, prev_path, nodeset, cur_node, exit_node, best_cost, best_node, d_cost, w_cost, u_cost)

        if all_node_visited(nodeset, knowledge):
            finished = True

        if len(prev_path) > 500:
            print(str(prev_path[-1]), str(prev_path[-2]), str(prev_path[-3]))
            raise Exception("Fall into infinite loop")
    return best_node, prev_path, back_steps

if __name__ == "__main__":

    # row, column, parking_row, parking_column
    row, column, parking_row, parking_column = 2, 2, 1, 1

    print("--- generate graph ---", datetime.datetime.now())
    nodeset, d_size, p_size, n_size = generate_graph(row, column, parking_row, parking_column)
    total_spots = d_size + p_size + n_size

    # nodeset = load_spot_graph("spot_graph")
    # total_spots = 179

    enter_node = nodeset[0]

    # center
    total_row = (1 + parking_column + 2) * row + 1
    total_col = (1 + parking_row + 2) * column + 1
    exit_node = nodeset[int(total_row / 2) * total_col + int(total_col / 2)]

    # drive cost of one spot distance
    d_cost = 1
    # walk cost of one spot distance
    w_cost = 4
    # u turn cost of one spot distance
    u_cost = 8

    # normal distribution sigma
    sigma = 1

    # all the paths between all node pairs
    drive_nodeset = [(key, val) for key, val in nodeset.items() if val.type == "D" or val.type == "C"]
    print("--- search all path in graph ---", datetime.datetime.now())
    all_pair = all_path(drive_nodeset)

    # used as threshold when entering the parking lot
    default_best_cost = 5 * (len(shortest_path(all_pair, enter_node, exit_node)) - 1) * w_cost

    # simple test

    # # occupancy density
    # density = 50
    # # stop forward search threshold
    # saving_threshold = 1
    # # visited node
    # knowledge = [-1] * 291
    # # used as threshold when entering the parking lot
    # default_best_cost = 250
    #
    # sigma = 1
    #
    # spot_map, spot_pdf = generate_gaussian_map(nodeset, all_pair, exit_node, sigma, density / 100, total_spots)
    #
    # for x in ["G", 0.1, 0.2, 0.3, 0.4, 0.5]:
    #     best_node, path, back_steps = execute(spot_map, nodeset, all_pair, knowledge, enter_node, exit_node,
    #                                             x, d_cost, w_cost, u_cost, default_best_cost, saving_threshold)
    #     print("Final:", path[-1], "ParkOption:", path[-1].empty_parking_spot(spot_map), "Length:", len(path),
    #           "BackSteps:", back_steps, "Cost:", total_cost(path, all_pair, exit_node, d_cost, w_cost, u_cost))
    #

    fo = open("2_2.txt", "w")
    fo.write(
        "map \t density \t saving_threshold \t x_value \t cost \t back_steps \t final_position \t final_parking_options \t path_length \t path \t map \n")

    for density in range(10, 100, 10):
        print("--- Density", density, datetime.datetime.now())
        print("     -- Progress [", end="", flush=True)
        for i in range(100):
            if i % 10 == 0:
                print("=", end="", flush=True)
            spot_map, spot_pdf = generate_gaussian_map(nodeset, all_pair, exit_node, sigma, density / 100, total_spots)
            xs = ["G", spot_pdf, 0.1, 0.2, 0.3, 0.4, 0.5]
            for saving_threshold in [2, 5, 10, 15, 20]:
                for j in range(len(xs)):
                    key = str(j) + str(saving_threshold)
                    knowledge = [-1] * total_spots
                    best_node, prev_path, back_steps = execute(spot_map, nodeset, all_pair, knowledge, enter_node,
                                                               exit_node, xs[j], d_cost, w_cost, u_cost,
                                                               default_best_cost, saving_threshold)
                    cost = total_cost(prev_path, all_pair, exit_node, d_cost, w_cost, u_cost)
                    # print("Final:", prev_path[-1], "ParkOption:", prev_path[-1].empty_parking_spot(spot_map), "Length:",
                    #       len(prev_path), "BackSteps:", back_steps, "Cost: ", cost)
                    fo.write(str([row, column, parking_row, parking_column])
                                + "\t" + str(density)
                                + "\t" + str(saving_threshold)
                                + "\t" + str(j)
                                + "\t" + str(cost)
                                + "\t" + str(back_steps)
                                + "\t" + str(prev_path[-1])
                                + "\t" + str(prev_path[-1].empty_parking_spot(spot_map))
                                + "\t" + str(len(prev_path))
                                + "\t" + str(list(map(lambda n: n.id, prev_path)))
                                + "\t" + str(spot_map) + "\n")
        print("]")
    fo.close()

