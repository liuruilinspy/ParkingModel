from simulation.node import Node


def generate_map(row, column, row_spots, column_spots):

    nodeset = {}

    total_row = (1 + column_spots + 2) * row + 1
    total_col = (1 + row_spots + 2) * column + 1
    square_width = 2 + row_spots
    square_height = 2 + column_spots

    rows = []
    for i in range(total_row):
        cur_row = get_row(i, square_width, square_height, total_col)
        for node in cur_row:
            nodeset[node.id] = node
        rows.append(cur_row)

    for i in range(total_row):
        for j in range(total_col):
            cur_node = nodeset[i * total_col + j]
            print(str(cur_node.id) + "-" + cur_node.type + "\t", end="")
            cur_node.parking_spots = set()
            cur_node.neighbors = set()
            if cur_node.type == "P" or cur_node.type == "N":
                continue
            neighbors = get_neighbor(i, j, total_row, total_col)
            for neigbr in neighbors:
                if nodeset[neigbr].type == "P":
                    cur_node.parking_spots.add(neigbr)
                elif nodeset[neigbr].type == "D":
                    cur_node.neighbors.add(neigbr)
        print()
    for key, val in nodeset.items():
        print(key, val.neighbors, val.parking_spots)

    for key, node in nodeset.items():
        if node.type == "C":
            del nodeset[key]
    return nodeset


def get_row(i, square_width, square_height, total_col):
    index = i % (square_height + 1)
    if index == 0:
        return empty_row(i, total_col)
    elif index == 1 or index == square_height:
        return side_row(i, square_width, total_col)
    else:
        return mid_row(i, square_width, total_col)


def side_row(i, square_width, total_col):
    cur_row = []
    for c in range(total_col):
        if c % (square_width + 1) == 0:
            cur_row.append(Node(i * total_col + c, "D"))
        elif c % (square_width + 1) == 1 or c % (square_width + 1) == square_width:
            cur_row.append(Node(i * total_col + c, "N"))
        else:
            cur_row.append(Node(i * total_col + c, "P"))
    return cur_row


def mid_row(i, square_width, total_col):
    cur_row = []
    for c in range(total_col):
        if c % (square_width + 1) == 0:
            cur_row.append(Node(i * total_col + c, "D"))
        elif c % (square_width + 1) == 1 or c % (square_width + 1) == square_width:
            cur_row.append(Node(i * total_col + c, "P"))
        else:
            cur_row.append(Node(i * total_col + c, "N"))
    return cur_row


def empty_row(i, total_col):
    cur_row = []
    for c in range(total_col):
        cur_row.append(Node(i * total_col + c, "D"))
    return cur_row

def get_neighbor(i, j, total_row, total_column):
    neighbors = []
    if i - 1 >= 0:
        neighbors.append(total_column * (i - 1) + j)
    if i + 1 <= total_row - 1:
        neighbors.append(total_column * (i + 1) + j)
    if j - 1 >= 0:
        neighbors.append(total_column * i + j - 1)
    if j + 1 <= total_column - 1:
        neighbors.append(total_column * i + j + 1)
    return neighbors


if __name__ == "__main__":
    nodeset = generate_map(1, 1, 2, 3)
