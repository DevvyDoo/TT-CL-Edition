from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
import HolidayDecorator
from toontown.toonbase import ToontownGlobals
from panda3d.core import Vec4, CSDefault, TransformState, NodePath, TransparencyAttrib
from panda3d.toontown import loadDNAFile
from toontown.hood import GSHood

class CrashedLeaderBoardDecorator(HolidayDecorator.HolidayDecorator):
    notify = DirectNotifyGlobal.directNotify.newCategory('CrashedLeaderBoardDecorator')

    def __init__(self):
        HolidayDecorator.HolidayDecorator.__init__(self)

    def decorate(self):
        self.updateHoodDNAStore()
        self.swapIval = self.getSwapVisibleIval()
        if self.swapIval:
            self.swapIval.start()
        if base.config.GetBool('want-crashedLeaderBoard-Smoke', 1):
            self.startSmokeEffect()

    def startSmokeEffect(self):
        if isinstance(base.cr.playGame.getPlace().loader.hood, GSHood.GSHood):
            base.cr.playGame.getPlace().loader.startSmokeEffect()

    def stopSmokeEffect(self):
        if isinstance(base.cr.playGame.getPlace().loader.hood, GSHood.GSHood):
            base.cr.playGame.getPlace().loader.stopSmokeEffect()

    def undecorate(self):
        if base.config.GetBool('want-crashedLeaderBoard-Smoke', 1):
            self.stopSmokeEffect()
        storageFile = base.cr.playGame.hood.storageDNAFile
        if storageFile:
            loadDNAFile(self.dnaStore, storageFile, CSDefault)
        self.swapIval = self.getSwapVisibleIval()
        if self.swapIval:
            self.swapIval.start()
