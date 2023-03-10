import DistributedTreasure
from panda3d.core import VBase3, VBase4
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpColorScaleInterval, LerpScaleInterval
from toontown.toonbase import ToontownGlobals

class DistributedSZTreasure(DistributedTreasure.DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.DistributedTreasure.__init__(self, cr)
        self.fadeTrack = None
        self.heartThrobIval = None
        self.accept('ValentinesDayStart', self.startValentinesDay)
        self.accept('ValentinesDayStop', self.stopValentinesDay)
        return

    def delete(self):
        DistributedTreasure.DistributedTreasure.delete(self)
        if self.fadeTrack:
            self.fadeTrack.finish()
            self.fadeTrack = None
        if self.heartThrobIval:
            self.heartThrobIval.finish()
            self.heartThrobIval = None
        self.ignore('ValentinesDayStart')
        self.ignore('ValentinesDayStop')
        return

    def setHolidayModelPath(self):
        self.defaultModelPath = self.modelPath

    def loadModel(self, modelPath, modelFindString = None):
        self.setHolidayModelPath()
        DistributedTreasure.DistributedTreasure.loadModel(self, self.modelPath, modelFindString)

    def startValentinesDay(self):
        newModelPath = 'phase_4/models/props/tt_m_ara_ext_heart'
        self.replaceTreasure(newModelPath)
        self.startAnimation()

    def stopValentinesDay(self):
        self.replaceTreasure(self.defaultModelPath)
        self.stopAnimation()

    def replaceTreasure(self, newModelPath):
        if self.fadeTrack:
            self.fadeTrack.finish()
            self.fadeTrack = None

        def replaceTreasureFunc(newModelPath):
            if self.nodePath == None:
                self.makeNodePath()
            else:
                self.treasure.getChildren().detach()
            model = loader.loadModel(newModelPath)
            model.instanceTo(self.treasure)
            return

        def getFadeOutTrack():
            fadeOutTrack = LerpColorScaleInterval(self.nodePath, 0.8, colorScale=VBase4(0, 0, 0, 0), startColorScale=VBase4(1, 1, 1, 1), blendType='easeIn')
            return fadeOutTrack

        def getFadeInTrack():
            fadeInTrack = LerpColorScaleInterval(self.nodePath, 0.5, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(0, 0, 0, 0), blendType='easeOut')
            return fadeInTrack

        base.playSfx(self.rejectSound, node=self.nodePath)
        self.fadeTrack = Sequence(getFadeOutTrack(), Func(replaceTreasureFunc, newModelPath), getFadeInTrack(), name=self.uniqueName('treasureFadeTrack'))
        self.fadeTrack.start()
        return

    def startAnimation(self):
        return
        
    def stopAnimation(self):
        if self.heartThrobIval:
            self.heartThrobIval.finish()
            self.heartThrobIval = None
        return
