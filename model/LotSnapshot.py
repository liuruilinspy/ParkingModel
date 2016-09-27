from model.TrackPath import TrackPath
from process.locationTranslate import locationTranslate
from util.simpleUtil import readParkingSpotCoordinate


class LotSnapshot:
    """
    Make the parking lots queriable anytime
    """

    def __init__(self, trackUpdate, trackMeta, trackPath, lotStatus):
        self._loaded = False
        self._frames = {}
        self._trackPath = {}
        self._trackMeta = trackMeta
        self.load(trackUpdate, trackMeta, trackPath, lotStatus)

    def load(self, trackUpdate, trackMeta, trackPath, lotStatus):
        """
        Load track info
        :param validTrack: park|leave behavior track
        :param trackMeta:
        :param trackPath:
        :return:
        """
        if not self._loaded:
            items = sorted(trackMeta.items(), key=lambda v: (v[1].timeSlot, v[1].endFrame))
            currentStatus = lotStatus.copy()
            it = iter(items)
            currentItem = next(it)
            currentFrame = 0

            while currentItem:
                if currentItem[1].timeSlot not in self._frames:
                    self._frames[currentItem[1].timeSlot] = []
                    currentFrame = 0
                self._frames[currentItem[1].timeSlot].append(currentStatus)
                if currentFrame == currentItem[1].endFrame:
                    if currentItem[1].id in trackUpdate:
                        if trackUpdate[currentItem[1].id] < 0:
                            currentStatus.setFree(-trackUpdate[currentItem[1].id])
                        else:
                            currentStatus.setOccupied(trackUpdate[currentItem[1].id])
                    currentItem = next(it, None)
                    if currentItem and currentItem[1].endFrame == currentFrame:
                        currentFrame -= 1
                currentFrame += 1
                currentStatus = currentStatus.copy()
            self.loadPath(trackPath, trackMeta, trackUpdate)
            self.loaded = True

    def loadPath(self, trackPath, trackMeta, trackUpdate):
        spots_dict = {}
        for key, val in trackUpdate.items():
            if key not in trackPath:
                print("No path found", key)
                continue
            if key == 1312:
                print("Found")
            file = "../data/20151102/test-" + trackMeta[key].timeSlot + "parkingSpots.xml"
            if file not in spots_dict:
                spots_dict[file] = readParkingSpotCoordinate(file)
            spots = spots_dict[file]
            path = TrackPath()
            for p in trackPath[key]:
                spot = locationTranslate(spots, p)
                path.append(spot)
            self._trackPath[key] = path

    def getStatusAtFrame(self, timeSlot, frame):
        try:
            return self._frames[timeSlot][frame].copy()
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
