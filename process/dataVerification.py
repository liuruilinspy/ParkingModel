import re

from util.simpleUtil import readLotsFromFile

"""
Verify if the parking/leaving behaviors conflict with current parking status
"""

def verifyLotConflict(initFile, updateFile):

    # initialize lots occupancy
    lotStatus = readLotsFromFile(initFile, 179)

    print("Initial lots: ", lotStatus.getRawList())
    print("With %d occupancy" % lotStatus.numOfOccupiedLots())

    # update lots occupancy
    try:
        fo = open("../data/"+updateFile, "r")
        lines = fo.readlines()
        count = 0
        for line in lines:
            result = re.search(r'(PARK|LEAVE) track=(\d+) spot= (\d+)', line, re.M|re.I)
            if result:
                count += 1
                if (result.group(1) == "PARK"):
                    if lotStatus.isFree(int(result.group(3))):
                        lotStatus.setOccupied(int(result.group(3)))
                    else:
                        print("Spot Conflict: [%s][%d] Track %s Park Spot %s" % (updateFile, count, result.group(2), result.group(3)))
                        return

                if (result.group(1) == "LEAVE"):
                    if not lotStatus.isFree(int(result.group(3))):
                        lotStatus.setFree(int(result.group(3)))
                    else:
                        print("Spot Conflict: [%s][%d] Track %s Leave Spot %s" % (updateFile, count, result.group(2), result.group(3)))
                        return
    except IOError:
        print(updateFile + " not found")
    finally:
        fo.close()

    print("Left lots: ", lotStatus)
    print("With %d occupancy" % lotStatus.numOfOccupiedLots())

    return lotStatus

def verifyLotOccupied(lotStatus, occupancyFile):
    """
    Verify if the parking status are consistent with the final video screenshot
    :param lotStatus:
    :param occupancyFile:
    :return:
    """
    # read lots from occupancy file
    verifiedSpot = readLotsFromFile(occupancyFile, 179).getRawList()

    rawList = lotStatus.getRawList()

    for i in range(len(rawList)):
        rawList[i] += verifiedSpot[i]

    NoErrorflag = True
    for i in rawList:
        if rawList[i] == 1:
            NoErrorflag = True
            print("Error spot: %d" % i)
    if NoErrorflag:
        print("No Error Found")
    return lotStatus

if __name__ == "__main__":
    lotStatus = verifyLotConflict("20151102/occupancy20151105_start.txt", "20151105/spot20151105.txt")
    verifyLotOccupied(lotStatus, "20151102/occupancy20151105_end.txt")
