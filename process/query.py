from model.LotSnapshot import LotSnapshot
from process.trackMerge import trackMergeTask
from util.simpleUtil import readTrackUpdateFile, readLotsFromFile

if __name__ == "__main__":
    trackMeta, trackPath = trackMergeTask("/Volumes/YuDriver/Parking/image_categoried/2015-11-02",
                                          "../data/20151102/track20151102.txt",
                                          "../data/20151102/spot20151102.txt",
                                          "../data/20151102/newTrack20151102.txt")
    trackUpdate = readTrackUpdateFile("../data/20151102/spot20151102.txt")
    lotStatus = readLotsFromFile("20151102/occupancy20151105_start.txt", 179)
    snapshot = LotSnapshot(trackUpdate, trackMeta, trackPath, lotStatus)

    track = snapshot.getTrackMeta(1)
    print(track)
    status = snapshot.getStatusAtFrame(track.timeSlot, track.startFrame)
    print(status.numOfOccupiedLots())
    print(snapshot.getTrackPath(1))
