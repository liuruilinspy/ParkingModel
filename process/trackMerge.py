import os, re

from model.Track import Track

def readTrackImageTitle(imagesDir):
    """
    Read track info from image titles
    :param imagesDir:
    :return: track metadata dictionary
    """
    seq = os.listdir(imagesDir)
    dict = {}
    for f in seq:
        # $name=test-(2015-11-02-07_25_06)$videobaseframe=200$startframe=336$endframe=454$startPosX=161$startPosY=9$endPosX=160$endPosY=549$track=1
        result = re.search(
            r'^(\$name=test-(\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_\d{2})\$videobaseframe=(\d+)\$startframe=(\d+)\$endframe=(\d+)\$startPosX=([0-9\-]+)\$startPosY=([0-9\-]+)\$endPosX=([0-9\-]+)\$endPosY=([0-9\-]+)\$track=(\d+))',
            f, re.I)
        if result:
            id = int(result.group(10))
            timeSlot = "test-" + result.group(2)
            startFrame = int(result.group(4))
            endFrame = int(result.group(5))
            startX = float(result.group(6))
            startY = float(result.group(7))
            endX = float(result.group(8))
            endY = float(result.group(9))
            track = Track(id, timeSlot, startFrame, endFrame, startX, startY, endX, endY)
            dict[id] = track
    return dict

def readTrackPath(pathFile, trackMetaDict):
    """
    Read track path from file
    :param pathFile:
    :param trackMetaDict : the dictionary for track meta data
    :return: track path dictionary
    """
    dict = {}
    fo = open(pathFile, "r")
    lines = fo.readlines()
    trackPath = []
    trackId = 0
    for line in lines:
        path = re.search(r'FINAL_OUTPUT: TRACK_HISTORY : TRACK \[ (\d+) \] POSITION= \( ([0-9\.]+) , ([0-9\.]+) \) FRAME= (\d+) ', line, re.I)
        if path:
            if int(path.group(1)) != trackId:
                dict[trackId] = list(trackPath)
                trackId = int(path.group(1))
                trackPath.clear()
            location = (float(path.group(2)), float(path.group(3)))
            trackPath.append(location)
        else:
            event = re.search(r'FINAL_OUTPUT: FRAME= (\d+) (LEAVING_EVENT: TRACK|PARKING_EVENT : TRACK |LEFT_EVENT: TRACK)\[ (\d+) \] (TAKES SPOT |IS LEAVING FROM SPOT|LEAVES FROM SPOT)\[ (\d+) \]', line.strip(), re.I)
            if event:
                metaTrackId = int(event.group(3))
                spotId = int(event.group(5))
                if metaTrackId not in trackMetaDict:
                    print("track " + str(metaTrackId) + " not in trackMetaDict")
                elif 'PARKING_EVENT' in line:
                    trackMetaDict[metaTrackId].type = 1
                    trackMetaDict[metaTrackId].spot = spotId
                elif 'LEAVING_EVENT' in line:
                    trackMetaDict[metaTrackId].type = 2
                    trackMetaDict[metaTrackId].spot = spotId
                elif 'LEFT_EVENT' in line:
                    trackMetaDict[metaTrackId].type = 3
                    trackMetaDict[metaTrackId].spot = spotId
    del dict[0]
    return dict

def trackMerge(trackFile, trackMeta, trackPath):
    """
    Merge track, update track metadata and track path
    :param trackFile: manual recorded track lots
    :param trackMeta: track metadata from image titles
    :param trackPath: track path positions
    :return: trackMeta and trackPath
    """
    fo = open(trackFile, "r")
    lines = fo.readlines()
    for line in lines:
        result = re.search(r'MERGE fromTrack= (\d+) toTrack= (\d+)', line, re.I)
        if result:
            # update track metadata
            if (int(result.group(1)) in trackMeta) & (int(result.group(2)) in trackMeta):
                fromTrack = trackMeta[int(result.group(1))]
                toTrack = trackMeta[int(result.group(2))]
                toTrack.preTrack = fromTrack.id
                fromTrack.nextTrack = toTrack.id
                #toTrack.startFrame = fromTrack.startFrame
                #toTrack.startX = fromTrack.startX
                #toTrack.startY = fromTrack.startY
                #toTrack.type += 10
                #fromTrack.type += 10
            # update track path
            # not every track is recorded
           # if (int(result.group(1)) in trackPath) & (int(result.group(2)) in trackPath):
                #fromTrack = trackPath[int(result.group(1))]
                #toTrack = trackPath[int(result.group(2))]
                #trackPath[int(result.group(2))] = fromTrack + toTrack
    return trackMeta, trackPath

def deleteRepeatedEndPosition(trackMeta, trackPath):
    """
    Delete unchanged positions in the end of the path
    :param trackPath:
    :return:
    """
    for key, val in trackPath.items():
        endPosition = val[len(val)-1]
        endIndex = len(val) - 1
        for i in reversed(range(len(val))):
            if val[i] != endPosition:
                break
            endIndex = i
        trackPath[key] = val[:endIndex + 1]
        if key in trackMeta:
            trackMeta[key].endFrame -= (len(val) - endIndex - 1)
    return trackPath

def deleteNotAppearedTrack(trackMeta, file):
    try:
        fo = open("../data/" + file, "r")
        lines = fo.readlines()
        for line in lines:
            result = re.search(r'(PARK|LEAVE) track=(\d+) spot= (\d+)', line, re.M | re.I)
    except IOError:
        print(file + " not found")
    finally:
        fo.close()

def listToDictByTimeAndId(alist):
    trackDict = {}
    for track in alist:
        key = track.id
        trackDict[key] = track
    return trackDict

def dictToList(dict):
    ilist = []
    for key, val in dict.items():
        ilist.append(val)
    return ilist

def addNewTrack(newTrackFile, trackMeta):
    """
    Add new tracks to track metadata
    :param newTrackFile:
    :return:
    """
    try:
        fo = open(newTrackFile, "r")
        lines = fo.readlines()
        for line in lines:
            result = re.search(
                r'(PARK|LEAVE) track=(\d+) spot= (\d+) endFrame=(\d+) timeslot=(\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_\d{2})', line, re.I)
            if result:
                id = int(result.group(2))
                timeSlot = result.group(5)
                endFrame = int(result.group(4))
                trackMeta[id] = Track(id, 'test-'+timeSlot, 0, endFrame, 0, 0, 0, 0)
        fo.close()
    except IOError:
        print(newTrackFile + " not found")
        return trackMeta
    finally:
        try:
            fo.close()
        except IOError:
            print(newTrackFile + " not found")

    return trackMeta

def trackMergeTask(trackImageDir, pathFile, lotFile, newTrackFile):
    """
    Combine all functions together
    :param trackImageDir: directory for all images
    :param pathFile: video log
    :param lotFile: manual log
    :param newTrackFile: manual added after conflict check (can be an empty file)
    :return:
    """
    meta = readTrackImageTitle(trackImageDir)
    path = readTrackPath(pathFile, meta)
    trackMeta, trackPath = trackMerge(lotFile, meta, path)
    addNewTrack(newTrackFile, trackMeta)
    return trackMeta, trackPath

if __name__ == "__main__":
    trackMeta, trackPath = trackMergeTask("/Volumes/YuDriver/Parking/image_categoried/2015-11-05",
                                          "../data/20151102/track20151105.txt",
                                          "../data/20151102/spot20151105.txt",
                                          "../data/20151102/newTrack20151105.txt")
    print(len(trackMeta), len(trackPath))
    print(trackMeta[7])
    print(trackPath[7])
    l = sorted(trackMeta.items(), key=lambda v: (v[1].timeSlot, v[1].endFrame))
    print(l)
