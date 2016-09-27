
def line(p1, p2):
    # Ax + By + C = 0
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, C

def isBetween(p, line1, line2):
    b1 = isAbove(p, line1)
    b2 = isBelow(p, line2)
    return b1 == b2

def isAbove(p, line):
    return line[0] * p[0] + line[1] * p[1] + line[2] <= 0

def isBelow(p, line):
    return line[0] * p[0] + line[1] * p[1] + line[2] >= 0

def isLeft(p, line):
    return isAbove(p, line)

def isRight(p, line):
    return isBelow(p, line)
