from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import BRTreasurePlannerAI
from toontown.toon import DistributedNPCFishermanAI

class BRHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BRHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.TheBrrrgh
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        self.treasurePlanner = BRTreasurePlannerAI.BRTreasurePlannerAI(self.zoneId)
        self.treasurePlanner.start()
