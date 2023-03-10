from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import MMTreasurePlannerAI
from toontown.safezone import DistributedMMPianoAI

class MMHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('MMHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.MinniesMelodyland
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        self.treasurePlanner = MMTreasurePlannerAI.MMTreasurePlannerAI(self.zoneId)
        self.treasurePlanner.start()
