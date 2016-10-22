import re
import xml.dom.minidom

from model.LotStatus import LotStatus
from model.Spot import Spot
from model.TimestampedEvent import TimestampedEvent


# file specify the spot availability configuration now
#   <record_42>
#    <spot_index>147</spot_index>
#    <spot_status>9</spot_status></record_42>
def readLotsFromFile(file, num):
    lotStatus = LotStatus(num)
    try:
        fo = open(file, "r")
        lines = fo.readlines()
        spotIndex = -1
        spotStatus = 0
        for line in lines:
            result = re.search(r'<(spot_index|spot_status)>(\d+)(</spot_index>|</spot_status></record_\d+>)', line.strip(), re.I)
            if result:
                if result.group(1) == "spot_index":
                    spotIndex = int(result.group(2))
                elif result.group(1) == "spot_status":
                    spotStatus = int(result.group(2))
                    if spotStatus != 0:
                        lotStatus.setOccupied(spotIndex)
    except IOError:
        print(file + " not found")
    return lotStatus

#update the track meta data using the file storing the manual correction from visual inspection
def readTrackUpdateFile(updateFile, trackMetaDict):
    try:
        fo = open(updateFile, "r")
        lines = fo.readlines()
        for line in lines:
            result = re.search(r'(PARK|LEAVE|FILL|EVACUATE) track=(\d+) spot= (\d+)', line, re.M | re.I)
            if result:
                trackId = int(result.group(2))
                spotId = int(result.group(3))
                if trackId not in trackMetaDict:
                    print("image not found: " + line)
                else:
                    if result.group(1) == "PARK":
                        trackMetaDict[trackId].type = 11  # 11 manually confirmed park
                        trackMetaDict[trackId].spot = spotId
                    elif result.group(1) == "LEAVE":
                        # this is some case where a track can be leaving and parking because tracks merged at the exit
                        if trackMetaDict[trackId].type < 10:
                            trackMetaDict[trackId].type = 12
                            trackMetaDict[trackId].spot = spotId
                        else:
                            trackMetaDict[trackId].evacuateList.append(spotId)
                    elif result.group(1) == "FILL":
                        trackMetaDict[trackId].fillList.append(spotId)  # the list of spot that is labeled as taken
                    elif result.group(1) == "EVACUATE":
                        trackMetaDict[trackId].evacuateList.append(spotId)  # the list of spot that is labeled as empty
    except IOError:
        print(updateFile + " not found")
    return trackMetaDict

def extractTimestampedEvent(trackMeta, trackPath, spotContourDic):
    events = []
    it = iter(trackMeta.items())
    currentTrack = next(it)
    while currentTrack:
        timeSlot = currentTrack[1].timeSlot
        id = currentTrack[1].id
        if currentTrack[1].type % 10 == 1:
            events.append(TimestampedEvent(timeSlot,currentTrack[1].endFrame, 1, currentTrack[1].spot, id))
        elif currentTrack[1].type % 10 == 2 or currentTrack[1].type % 10 == 3:
            events.append(TimestampedEvent(timeSlot, currentTrack[1].startFrame, -1, currentTrack[1].spot, id))
        for spot in currentTrack[1].fillList:
            events.append(TimestampedEvent(timeSlot, currentTrack[1].endFrame, 1, spot, id))
        for spot in currentTrack[1].evacuateList:
            events.append(TimestampedEvent(timeSlot, currentTrack[1].endFrame, -1, currentTrack[1].spot, id))
        currentTrack = next(it, None)

    return events

def readParkingSpotCoordinate(file):
    spots = {}
    # test-2015-11-02-07_25_06occupancy.xml
    timestamp = file[-35:-16]
    print("reading spot configuration for ", timestamp)
    try:
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        for i in range(179):
            spot = collection.getElementsByTagName("spot_" + str(i))
            raw = spot[0].childNodes[0].data
            raw = raw.replace("\n", "")
            ts = raw.split(" ")
            spots[i] = list(map(int, ts[12:20]))
    except IOError:
        print(file + " not found")
    spots_obj = {}
    for key, val in spots.items():
        spot = Spot().set_timestamp(timestamp).set_id(key).set_type(0)
        if key < 29 or (key > 61 and key < 95) or (key > 125 and key < 156):
            spot.set_upper_left([val[0], val[1]]) \
                .set_lower_left([val[2], val[3]]) \
                .set_lower_right([val[4], val[5]]) \
                .set_upper_right([val[6], val[7]])
        else:
            spot.set_upper_left([val[6], val[7]]) \
                .set_lower_left([val[4], val[5]]) \
                .set_lower_right([val[2], val[3]]) \
                .set_upper_right([val[0], val[1]])
        spots_obj[key] = spot
    return spots_obj

if __name__ == "__main__":
    print(readParkingSpotCoordinate("../data/20151102/test-2015-11-02-07_25_06parkingSpots.xml")[0])