class Track:

    def __init__(self, id, timeSlot, startFrame, endFrame, startX, startY, endX, endY):
        self.id = id
        self.timeSlot = timeSlot
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.startX = startX        # start position X
        self.startY = startY        # start position Y
        self.endX = endX            # end position X
        self.endY = endY            # end position Y
        self.fillList = []          # the list of spot that is labeled as taken
        self.evacuateList = []      # the list of spot that is labeled as empty
        self.type = 0               # 0 initial, 1 auto-detected park, 2 auto-detected leaving, 3 auto-detected left, +10 confirmed
        self.spot = -1              # the assoicated spot, -1 means no spot
        self.preTrack = -1
        self.nextTrack = -1

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self.id == other.id & self.timeSlot == other.timeSlot & self.endFrame == other.endFrame

    def __lt__(self, other):
        assert isinstance(other, self.__class__)
        return self.timeSlot + str(self.endFrame) < other.timeSlot + str(other.endFrame)

    def __gt__(self, other):
        assert isinstance(other, self.__class__)
        return self.timeSlot + str(self.endFrame) > other.timeSlot + str(other.endFrame)

    def __str__(self):
        return "{" + \
            "id: " + str(self.id) + ", " + \
            "timeSlot: " + self.timeSlot + ", " + \
            "startFrame: " + str(self.startFrame) + ", " + \
            "endFrame: " + str(self.endFrame) + ", " + \
            "start: " + str((self.startX, self.startY)) + ", " + \
            "end: " + str((self.endX, self.endY)) + "}"
