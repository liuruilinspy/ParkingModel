class Node:

    def __init__(self, id):
        # node id
        self.id = id

    def empty_parking_slot(self, spot_map):
        s = []
        for spot in self.parking_spots:
            if spot_map[spot] == 0:
                s.append(spot)
        return s

    def __str__(self):
        return str(self.id)

    def copy(self):
        new_node = Node(self.id)
        if hasattr(self, "neighbors"):
            new_node.neighbors = list(self.neighbors)
        if hasattr(self, "parking_spots"):
            new_node.parking_spots = list(self.parking_spots)
        return new_node
