from DistributedToonInteriorAI import *
from toontown.toonbase import ToontownGlobals

class DistributedToonHallInteriorAI(DistributedToonInteriorAI):

    def __init__(self, block, air, zoneId, building):
        DistributedToonInteriorAI.__init__(self, block, air, zoneId, building)
        self.accept('ToonEnteredZone', self.logToonEntered)
        self.accept('ToonLeftZone', self.logToonLeft)

    def logToonEntered(self, avId, zoneId):
        result = self.getCurPhase()
        if result == -1:
            phase = 'not available'
        else:
            phase = str(result)
        self.air.writeServerEvent('sillyMeter', avId, 'enter|%s' % phase)

    def logToonLeft(self, avId, zoneId):
        result = self.getCurPhase()
        if result == -1:
            phase = 'not available'
        else:
            phase = str(result)
        self.air.writeServerEvent('sillyMeter', avId, 'exit|%s' % phase)

    def getCurPhase(self):
        result = -1
        enoughInfoToRun = False
        return result

    def delete(self):
        self.ignoreAll()
        DistributedToonInteriorAI.delete(self)
