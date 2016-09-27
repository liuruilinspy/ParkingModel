"""
Translate spots and vehicles coordinates into that on the standard map
"""
import os
import re

from model.Spot import Spot
from util.geometryUtil import isBetween, line, isAbove, isBelow
from util.simpleUtil import readParkingSpotCoordinate



def locationTranslate(spots, p):
    """
    Translate location pixels to standard spots id.
    Do not modify this function unless you fully understand how it work
    :param spots:
    :param p:
    :return:
    """

    # parking spots
    for key, spot in spots.items():
        if spot.isInside(p):
            return spot

    # path spots
    # first column (179)
    if isBetween(p, line(spots[0].upper_left, spots[28].lower_left),
                 line(spots[0].upper_right, spots[28].lower_right)):
        return Spot().set_id(179).set_type(1).set_timestamp(spots[0].timestamp)

    # second column (180 - 214)
    if isBetween(p, line(spots[0].upper_right, spots[28].lower_right),
                 line(spots[29].upper_left, spots[61].lower_left)):
        if isAbove(p, line(spots[29].upper_left, spots[62].upper_right)):
            # spot 180
            return Spot().set_id(180).set_type(1).set_timestamp(spots[0].timestamp)
        for i in range(181, 214):
            # spot 181 - 213
            if isBetween(p, line(spots[i - 152].upper_left, spots[i - 119].upper_right), line(spots[i - 151].lower_left, spots[i - 119].lower_right)):
                return Spot().set_id(i).set_type(1).set_timestamp(spots[0].timestamp)
        if isBelow(p, line(spots[61].lower_left, spots[94].lower_right)):
            # spot 214
            return Spot().set_id(214).set_type(1).set_timestamp(spots[0].timestamp)

    # third column (215, 216)
    if isBetween(p, line(spots[29].upper_left, spots[61].lower_left),
                 line(spots[29].upper_right, spots[61].lower_right)):
        if isAbove(p, line(spots[29].upper_left, spots[29].upper_right)):
            # spot 215
            return Spot().set_id(215).set_type(1).set_timestamp(spots[0].timestamp)
        if isBelow(p, line(spots[61].lower_left, spots[61].lower_right)):
            # spot 216
            return Spot().set_id(216).set_type(1).set_timestamp(spots[0].timestamp)

    # fourth column (217, 218)
    if isBetween(p, line(spots[62].upper_left, spots[94].lower_left),
                 line(spots[62].upper_right, spots[94].lower_right)):
        if isAbove(p, line(spots[62].upper_left, spots[62].upper_right)):
            # spot 217
            return Spot().set_id(217).set_type(1).set_timestamp(spots[0].timestamp)
        if isBelow(p, line(spots[94].lower_left, spots[94].lower_right)):
            # spot 218
            return Spot().set_id(218).set_type(1).set_timestamp(spots[0].timestamp)

    # fifth column (219 - 253)
    if isBetween(p, line(spots[62].upper_right, spots[94].lower_right),
                 line(spots[95].upper_left, spots[125].lower_left)):

        for i in range(219, 222):
            # spot 219, 220, 221
            if isAbove(p, line(spots[i - 157].upper_left, spots[i - 157].upper_right)):
                return Spot().set_id(i).set_type(1).set_timestamp(spots[0].timestamp)

        for i in range(222, 253):
            # spot 222 - 252
            if isBetween(p, line(spots[i - 158].upper_left, spots[i - 127].upper_right),
                         line(spots[i - 158].lower_left, spots[i - 127].lower_right)):
                return Spot().set_id(i).set_type(1).set_timestamp(spots[0].timestamp)

        if isBelow(p, line(spots[94].lower_left, spots[125].lower_right)):
            # spot 253
            return Spot().set_id(253).set_type(1).set_timestamp(spots[0].timestamp)

    # sixth column (254, 255)
    if isBetween(p, line(spots[95].upper_left, spots[125].lower_left),
                 line(spots[95].upper_right, spots[125].lower_right)):
        if isAbove(p, line(spots[95].upper_left, spots[95].upper_right)):
            # spot 254
            return Spot().set_id(254).set_type(1).set_timestamp(spots[0].timestamp)
        if isBelow(p, line(spots[125].lower_left, spots[125].lower_right)):
            # spot 255
            return Spot().set_id(255).set_type(1).set_timestamp(spots[0].timestamp)

    # seventh column (256, 257)
    if isBetween(p, line(spots[126].upper_left, spots[155].lower_left),
                 line(spots[126].upper_right, spots[155].lower_right)):
        if isAbove(p, line(spots[126].upper_left, spots[126].upper_right)):
            # spot 256
            return Spot().set_id(256).set_type(1).set_timestamp(spots[0].timestamp)
        if isBelow(p, line(spots[155].lower_left, spots[155].lower_right)):
            # spot 257
            return Spot().set_id(257).set_type(1).set_timestamp(spots[0].timestamp)

    # eighth column (258 - 289)
    if isBetween(p, line(spots[126].upper_right, spots[155].lower_right),
                 line(spots[156].upper_left, spots[178].lower_left)):
        if isAbove(p, line(spots[126].upper_left, spots[126].upper_right)):
            # spot 258
            return Spot().set_id(258).set_type(1).set_timestamp(spots[0].timestamp)

        for i in range(259, 289):
            # spot 259 - 288
            if isBetween(p, line(spots[i - 133].upper_left, spots[i - 133].upper_right),
                         line(spots[i - 133].lower_left, spots[i - 133].lower_right)):
                return Spot().set_id(i).set_type(1).set_timestamp(spots[0].timestamp)

        if isBelow(p, line(spots[155].lower_left, spots[155].lower_right)):
            # spot 289
            return Spot().set_id(289).set_type(1).set_timestamp(spots[0].timestamp)

    # ninth column (290)
    if isBetween(p, line(spots[156].upper_left, spots[178].lower_left),
                 line(spots[156].upper_right, spots[178].lower_right)):
        return Spot().set_id(290).set_type(1).set_timestamp(spots[0].timestamp)

    return Spot()

def trackTimeSlotDivision(imagesDir):
    """
    Divide track number according to time slot
    :param imagesDir:
    :return: starting track id of each time slot
    """
    seq = os.listdir(imagesDir)
    division = {}
    for f in seq:
        # $name=test-(2015-11-02-07_25_06)$videobaseframe=200$startframe=336$endframe=454$startPosX=161$startPosY=9$endPosX=160$endPosY=549$track=1
        result = re.search(
            r'^(\$name=test-(\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_\d{2})\$videobaseframe=(\d+)\$startframe=(\d+)\$endframe=(\d+)\$startPosX=(\d+)\$startPosY=(\d+)\$endPosX=(\d+)\$endPosY=(\d+)\$track=(\d+))',
            f, re.M | re.I)
        if result:
            trackId = result.group(10)
            if result.group(2) not in division:
                division[result.group(2)] = trackId
            else:
                if division[result.group(2)] > trackId:
                    # update track id to minimum
                    division[result.group(2)] = trackId
    return division

# trackTimeSlotDivision("/Volumes/YuDriver/Parking/image_categoried/2015-11-02")

if __name__ == "__main__":
    # spots = readParkingSpotCoordinate("../data/20151102/test-2015-11-02-07_25_06parkingSpots.xml")
    # print(locationTranslate(spots, (60, 20)))     # 0 0
    # print(locationTranslate(spots, (73, 80)))     # 29 1
    #
    # print(locationTranslate(spots, (70, 50)))     # 1 1
    # print(locationTranslate(spots, (93, 600)))    # 35 1
    #
    # print(locationTranslate(spots, (340, 440)))    # 178 0
    spots = readParkingSpotCoordinate("../data/20151102/test-2015-11-02-09_25_07parkingSpots.xml")
    s = locationTranslate(spots, (173.081, 87.7176))
    x = s.copy()
    print(x)