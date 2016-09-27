"""
Park lots status
"""

class LotStatus:

    def __init__(self, num):
        self._num = 0                # total number of parking lots
        self._occupiedLots = 0       # occupied parking lots
        self._freeLots = 0           # free parking lots
        self._lots = [0] * num  # parking lots list: 0 for free and 1 for occupied

    def isFree(self, id):
        """
        Return if the parking lot is available
        :param id: parking lot id
        :return:
        """
        try:
            return self._lots[id] == 0
        except (TypeError, IndexError):
            print("Error index: illegal type or out of bound ", id)

    def setOccupied(self, id):
        try:
            self._lots[id] = 1
            self._freeLots -= 1
            self._occupiedLots += 1
        except (TypeError, IndexError):
            print("Error index: illegal type or out of bound ", id)

    def setFree(self, id):
        try:
            self._lots[id] = 0
            self._freeLots += 1
            self._occupiedLots -= 1
        except (TypeError, IndexError):
            print("Error index: illegal type or out of bound", id)

    def update(self):
        """
        Update counter
        :return:
        """
        count = 0
        occupied = 0
        for l in self.lots:
            count += 1
            occupied += l
        self.num = count
        self.freeLots = count - occupied
        self._occupiedLots = occupied

    def getRawList(self):
        return list(self._lots)

    def numOfFreeLots(self):
        return self._freeLots

    def numOfOccupiedLots(self):
        return self._occupiedLots

    def copy(self):
        """
        LotStatus deep copy
        :return: copy of current status
        """
        copy = LotStatus(self._num)
        copy._occupiedLots = self._occupiedLots
        copy._freeLots = self._freeLots
        copy._lots = list(self._lots)
        return copy

    def __str__(self):
        return str(self._lots)