from model.LotSnapshot import LotSnapshot
from process.trackMerge import trackMergeTask
from util.simpleUtil import readTrackUpdateFile, readLotsFromFile

if __name__ == "__main__":
    trackMeta, trackPath = trackMergeTask("C:/Users/Ruilin/Documents/GitHub/vehicleTracking/images/20150420-1102-1111-1119/20151102",
                                          "../data/20151102/track20151102.txt",
                                          "../data/20151102/spot20151102.txt",
                                          "../data/20151102/newTrack20151102.txt")
    trackUpdateMeta = readTrackUpdateFile("../data/20151102/spot20151102.txt", trackMeta)
    snapshot = LotSnapshot(trackUpdateMeta, trackPath, "../data/20151102/")

    track = snapshot.getTrackMeta(1)
    print(track)
    status = snapshot.getStatusAtFrame(track.timeSlot, track.startFrame)
    print(status.numOfOccupiedLots())
    print(snapshot.getTrackPath(1))