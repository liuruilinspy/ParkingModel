from model.TrackPath import TrackPath
from process.locationTranslate import locationTranslate
from util.simpleUtil import readParkingSpotCoordinate, readLotsFromFile, extractTimestampedEvent


# Make the parking lots query possible at anytime
class LotSnapshot:
    lotSize = 179
    def __init__(self, trackMeta, trackPath, configPathPrefix):
        self._loaded = False
        self._frames = {}
        self._trackPath = {}
        self._trackMeta = trackMeta
        self._lotConfigDir = configPathPrefix
        self.load(trackMeta, trackPath)

    def loadPath(self, trackPath, trackMeta):
        spots_dict = {}
        for trackId, track in trackMeta.items():
            if track.type % 10 != 1:
                continue
            if trackId not in trackPath:
                print("No path found", trackId)
                continue
            if trackId == 1312:
                print("Found")
            if trackMeta[trackId].timeSlot not in spots_dict:
                spotsContourFile = self._lotConfigDir + trackMeta[trackId].timeSlot + "parkingSpots.xml"
                spots_dict[trackMeta[trackId].timeSlot] = readParkingSpotCoordinate(spotsContourFile)
            spots = spots_dict[trackMeta[trackId].timeSlot]
            path = TrackPath()
            for p in trackPath[trackId]:
                spot = locationTranslate(spots, p)
                path.append(spot)
            self._trackPath[trackId] = path

    def load(self, trackMeta, trackPath):
        """
        Load track info
        :param trackMeta:
        :param trackPath:
        :return:
        """
        if self._loaded:
            return

        #self.loadPath(trackPath, trackMeta)
        events = extractTimestampedEvent(trackMeta, trackPath, {})
        items = sorted(events, key=lambda v: (v.timeSlot, v.frame))
        it = iter(items)
        currentEvent = next(it)
        currentFrame = 0
        currentSlot = None
        currentStatus = None
        eventCount = 0
        while currentEvent:
            if currentEvent.timeSlot not in self._frames:
                self._frames[currentEvent.timeSlot] = {}
                newSlotStatus = readLotsFromFile(
                    self._lotConfigDir + currentEvent.timeSlot + "occupancy.xml",
                    LotSnapshot.lotSize)
                if currentStatus and currentSlot:
                    print("Disagreement= " + str(newSlotStatus.compare(currentStatus))
                          + " Event count= " + str(eventCount))
                    self._frames[currentSlot][currentFrame] = currentStatus
                currentStatus = newSlotStatus
                currentSlot = currentEvent.timeSlot
                currentFrame = 0
                eventCount = 0

            if currentFrame < currentEvent.frame:
                self._frames[currentEvent.timeSlot][currentFrame] = currentStatus
                currentStatus = currentStatus.copy()
                currentFrame = currentEvent.frame

            if currentFrame == currentEvent.frame:
                eventCount += 1
                if currentEvent.operation < 0:
                    currentStatus.setFree(currentEvent.spot)
                else:
                    currentStatus.setOccupied(currentEvent.spot)
                currentEvent = next(it, None)

        if currentStatus and currentSlot:
            self._frames[currentSlot][currentFrame] = currentStatus
        self.loaded = True

    def getStatusAtFrame(self, timeSlot, frame):
        try:
            state_index = 0
            # since there are usually <100 events in each slot, we don't use linear search instead of binary search
            for key, value in self._frames[timeSlot].items():
                if state_index < key <= frame:
                    state_index = key
            return self._frames[timeSlot][state_index].copy()
        except IndexError:
            print("Wrong timeSlot/frame number")

    def getTrackPath(self, trackId):
        try:
            return self._trackPath[trackId]
        except KeyError:
            print("No such a key", trackId)

    def getTrackMeta(self, trackId):
        try:
            return self._trackMeta[trackId]
        except KeyError:
            print("No such a key", trackId)
