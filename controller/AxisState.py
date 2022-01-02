class AxisState(object):
    _value = None
    _vector = 0

    VALUE_LOW_INDEX = 0
    VALUE_UNSET_INDEX = 1
    VALUE_HIGH_INDEX = 2

    def __init__(self, values = [True, None, False]):
        super().__init__()
        self.values = values
        self._value = values[self.VALUE_UNSET_INDEX]
    
    def isActive(self):
        return (self._value != self.values[self.VALUE_UNSET_INDEX])
    
    def isInactive(self):
        return not self.isActive()
    
    def isLow(self):
        return (self._value == self.values[self.VALUE_LOW_INDEX])
    
    def isHigh(self):
        return (self._value == self.values[self.VALUE_HIGH_INDEX])
    
    def isUnset(self):
        return self.isInactive()

    def setLow(self):
        self._value = self.values[self.VALUE_LOW_INDEX]
    
    def setHigh(self):
        self._value = self.values[self.VALUE_HIGH_INDEX]
    
    def unset(self):
        self._value = self.values[self.VALUE_UNSET_INDEX]
    
    def getRawValue(self):
        return self._value

    def setRawVector(self, vector):
        self._vector = vector
    
    def getRawVector(self):
        return self._vector
    
    def getVector(self):
        return abs(self.getRawVector())
