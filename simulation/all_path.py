from simulation.generate_graph import generate_graph
from simulation.search7 import all_path

import pickle

if __name__ == "__main__":
    row, column, parking_row, parking_column = 2, 2, 10, 20
    print("-----Start", row, column, "-----")
    nodeset, d_size, p_size, n_size = generate_graph(row, column, parking_row, parking_column)
    drive_nodeset = [(key, val) for key, val in nodeset.items() if val.type == "D"]
    all_pair = all_path(drive_nodeset)
    f = str(row)+"_"+str(column)+".pkl"
    output = open(f, 'wb')
    pickle.dump(all_pair, output)

    row, column, parking_row, parking_column = 4, 4, 10, 20
    print("-----Start", row, column, "-----")
    nodeset, d_size, p_size, n_size = generate_graph(row, column, parking_row, parking_column)
    drive_nodeset = [(key, val) for key, val in nodeset.items() if val.type == "D"]
    all_pair = all_path(drive_nodeset)
    f = str(row) + "_" + str(column) + ".pkl"
    output = open(f, 'wb')
    pickle.dump(all_pair, output)

    row, column, parking_row, parking_column = 8, 8, 10, 20
    print("-----Start", row, column, "-----")
    nodeset, d_size, p_size, n_size = generate_graph(row, column, parking_row, parking_column)
    drive_nodeset = [(key, val) for key, val in nodeset.items() if val.type == "D"]
    all_pair = all_path(drive_nodeset)
    f = str(row) + "_" + str(column) + ".pkl"
    output = open(f, 'wb')
    pickle.dump(all_pair, output)

