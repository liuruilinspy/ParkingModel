class TrackPath:

    def __init__(self):
        self._path = []

    def append(self, spot):
        self._path.append(spot)
        return self

    def spotAt(self, frame):
        try:
            return self._path[frame].copy()
        except IndexError:
            print("Wrong frame")

    def pathLen(self):
        return len(self._path)

    def __str__(self):
        path_str = []
        for p in self._path:
            if p.id != -1:
                path_str.append(str(p.id))
            else:
                path_str.append("_")
        return str(list)

