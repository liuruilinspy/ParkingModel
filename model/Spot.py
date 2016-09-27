from util.geometryUtil import isBetween, line


class Spot:

    def __init__(self):
        self.id = -1
        self.type = -1
        self.timestamp = ""
        self.upper_left = ()
        self.upper_right = ()
        self.lower_left = ()
        self.lower_right = ()

    def set_id(self, i):
        self.id = i
        return self

    def set_upper_left(self, p):
        self.upper_left = p
        return self

    def set_upper_right(self, p):
        self.upper_right = p
        return self

    def set_lower_left(self, p):
        self.lower_left = p
        return self

    def set_lower_right(self, p):
        self.lower_right = p
        return self

    def set_type(self, type):
        self.type = type
        return self

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
        return self

    def isInside(self, p):
        return isBetween(p, line(self.upper_left, self.lower_left), line(self.upper_right, self.lower_right)) \
               and isBetween(p, line(self.upper_left, self.upper_right), line(self.lower_left, self.lower_right))

    def copy(self):
        newSpot = Spot()
        newSpot.set_upper_left(tuple(self.upper_left))
        newSpot.set_upper_right(tuple(self.upper_right))
        newSpot.set_lower_left(tuple(self.lower_left))
        newSpot.set_lower_right(tuple(self.lower_right))
        newSpot.set_timestamp(self.timestamp)
        newSpot.set_type(self.type)
        newSpot.set_id(self.id)
        return newSpot

    def __str__(self):
        if self.id == -1:
            return "{_}"
        else:
            return "{id: " + str(self.id) + ", timestamp: " + self.timestamp + ", type: " \
                   + str(self.type) + ", " + str(self.upper_left) + ", " + str(self.lower_left) \
                   + ", " + str(self.lower_right) + ", " + str(self.upper_right) + "}"
