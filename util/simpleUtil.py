import re
import xml.dom.minidom

from model.LotStatus import LotStatus
from model.Spot import Spot


def readLotsFromFile(file, num):
    lotStatus = LotStatus(num)
    try:
        fo = open("../data/" + file, "r")
        lines = fo.readlines()
        for line in lines:
            result = re.search(r'(^\d+$)', line, re.M | re.I)
            if result:
                lotStatus.setOccupied(int(result.group(1)))
    except IOError:
        print(file + " not found")
    return lotStatus


def readTrackUpdateFile(updateFile):
    trackUpdate = {}
    try:
        fo = open(updateFile, "r")
        lines = fo.readlines()
        count = 0
        for line in lines:
            result = re.search(r'(PARK|LEAVE) track=(\d+) spot= (\d+)', line, re.M | re.I)
            if result:
                count += 1
                if result.group(1) == "PARK":
                    trackUpdate[int(result.group(2))] = int(result.group(3))
                if result.group(1) == "LEAVE":
                    trackUpdate[int(result.group(2))] = -int(result.group(3))
    except IOError:
        print(updateFile + " not found")
    return trackUpdate


def readParkingSpotCoordinate(file):
    spots = {}
    # test-2015-11-02-07_25_06occupancy.xml
    timestamp = file[-35:-16]
    print(timestamp)
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