import datetime

from simulation.generate_graph import generate_graph
from simulation.search8 import all_path, generate_gaussian_map, execute, total_cost, ground_truth

if __name__ == "__main__":
    # row, column, parking_row, parking_column
    row, column, parking_row, parking_column = 4, 4, 10, 20

    print("-- generate graph --", datetime.datetime.now())
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
    d_cost = 1.63
    # walk cost of one spot distance
    w_cost = 5.27
    # u turn cost of one spot distance
    u_cost = 5.27 * 2.5

    # normal distribution sigma
    sigma = 1

    # all the paths between all node pairs
    drive_nodeset = [(key, val) for key, val in nodeset.items() if val.type == "D" or val.type == "C"]
    print("-- search all path in graph --", datetime.datetime.now())
    all_pair = all_path(drive_nodeset)

    # used as threshold when entering the parking lot
    default_best_cost = (len(drive_nodeset) - 1) * w_cost

    fo = open("4_4/4_4.txt", "w")
    fo.write(
        "map \t density \t saving_threshold \t x_value \t cost \t cost-truth \t back_steps \t final_position \t final_parking_options \t path_length \t path \t map \n")
    for saving_threshold in [2 * w_cost, 4 * w_cost, 6 * w_cost]:
        f_cost = open("4_4/4_4_cost_" + str(saving_threshold)+".txt", "w")
        f_cost.write("density \t ground_truth \t historical \t 10% \t 20% \t 30% \t 40% \t 50% \n")
        print("-- Threshold", saving_threshold)
        for density in range(10, 100, 10):
            print("  -- Density", density, datetime.datetime.now())
            print("    -- Progress [", end="", flush=True)

            for i in range(100):
                if i % 10 == 0:
                    print("=", end="", flush=True)
                spot_map, spot_pdf = generate_gaussian_map(nodeset, all_pair, exit_node, sigma, density / 100,
                                                           total_spots)
                xs = ["G", spot_pdf, 0.1, 0.2, 0.3, 0.4, 0.5]
                truth = 0
                print_result = []
                for j in range(len(xs)):
                    key = str(j) + str(saving_threshold)
                    knowledge = [-1] * total_spots
                    if j == 0:
                        best_node, prev_path, back_steps = ground_truth(drive_nodeset, all_pair, spot_map, enter_node,
                                                                        exit_node, d_cost, w_cost)
                    else:
                        best_node, prev_path, back_steps = execute(spot_map, nodeset, all_pair, knowledge, enter_node,
                                                                   exit_node, xs[j], d_cost, w_cost, u_cost,
                                                                   default_best_cost, saving_threshold)

                    cost = total_cost(prev_path, all_pair, exit_node, d_cost, w_cost, u_cost)
                    if j == 0:
                        truth = cost
                        print_result.append(truth)
                    else:
                        print_result.append(cost - truth)
                    # print("Final:", prev_path[-1], "ParkOption:", prev_path[-1].empty_parking_spot(spot_map), "Length:",
                    #       len(prev_path), "BackSteps:", back_steps, "Cost: ", cost)
                    fo.write(str([row, column, parking_row, parking_column])
                             + "\t" + str(density)
                             + "\t" + str(saving_threshold)
                             + "\t" + str(j)
                             + "\t" + str(cost)
                             + "\t" + str(cost - truth)
                             + "\t" + str(back_steps)
                             + "\t" + str(prev_path[-1])
                             + "\t" + str(prev_path[-1].empty_parking_spot(spot_map))
                             + "\t" + str(len(prev_path))
                             + "\t" + str(list(map(lambda n: n.id, prev_path)))
                             + "\t" + str(spot_map) + "\n")

                f_cost.write(str(density)
                             + "\t"
                             + "\t".join(map(str, print_result))
                             + "\n")
            print("]")
        f_cost.close()
    fo.close()
