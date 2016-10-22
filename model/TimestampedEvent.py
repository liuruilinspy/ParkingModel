class TimestampedEvent:

    def __init__(self, time_slot, frame, operation, spot, track):
        self.timeSlot = time_slot
        self.frame = frame
        self.operation = operation
        self.spot = spot
        self.track = track
