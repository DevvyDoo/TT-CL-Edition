from direct.distributed.ClockDelta import *
from direct.fsm import FSM
from toontown.coghq import DistributedCashbotBossCrane
from toontown.coghq import DistributedCashbotBossSafe
from panda3d.core import *

from toontown.suit import DistributedCashbotBossGoon


class DistributedCashbotBossSideCrane(DistributedCashbotBossCrane.DistributedCashbotBossCrane, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCashbotBossCrane')
    firstMagnetBit = 21
    craneMinY = 8
    craneMaxY = 30
    armMinH = -12.5
    armMaxH = 12.5
    shadowOffset = 1
    emptyFrictionCoef = 0.1
    emptySlideSpeed = 15
    emptyRotateSpeed = 20
    lookAtPoint = Point3(0.3, 0, 0.1)
    lookAtUp = Vec3(0, -1, 0)
    neutralStickHinge = VBase3(0, 90, 0)
    magnetModel = loader.loadModel('phase_10/models/cogHQ/CBMagnet.bam')

    def __init__(self, cr):
        DistributedCashbotBossCrane.DistributedCashbotBossCrane.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedCashbotBossSideCrane')

    def getName(self):
        return 'SideCrane-%s' % self.index
        
    def grabObject(self, obj):
        DistributedCashbotBossCrane.DistributedCashbotBossCrane.grabObject(self, obj)

    def sniffedSomething(self, entry):
    
        # Something was sniffed as grabbable.
        np = entry.getIntoNodePath()
        
        if np.hasNetTag('object'):
            doId = int(np.getNetTag('object'))
        else:
            self.notify.warning("%s missing 'object' tag" % np)
            return
            
        self.notify.debug('sniffedSomething %d' % doId)

        obj = base.cr.doId2do.get(doId)
        if obj.state == 'Grabbed':
            return
  
        # Spawn protection
        if obj.state in ['EmergeA', 'EmergeB']:
            return
        
        if obj and obj.state != 'LocalDropped' and (obj.state != 'Dropped' or obj.craneId != self.doId):
            self.boss.craneStatesDebug(doId=self.doId, content='Sniffed something, held obj %s' % (
                self.heldObject.getName() if self.heldObject else "Nothing"))
            
            if isinstance(obj, DistributedCashbotBossSafe.DistributedCashbotBossSafe):
                # To-Do
                return
            
            self.considerObjectState(obj)
            obj.d_requestGrab()
            #state_logger.info(f"[Client] [Crane-{self.doId}], AvId-{self.avId}, Current State: {self.state}, sniffedSomething - requesting object Grab, obj.requestGrab()")
            # See if we should do anything with this object when sniffing it
            obj.demand('LocalGrabbed', localAvatar.doId, self.doId)
            #state_logger.info(f"[Client] [Crane-{self.doId}], AvId-{self.avId}, Current State: {self.state}, sniffedSomething - demanding object LocalGrabbed, obj.demand(...)"), 

    def getPointsForStun(self):
        return self.boss.ruleset.POINTS_SIDESTUN

    # Override base method, always wake up goons
    def considerObjectState(self, obj):
        if isinstance(obj, DistributedCashbotBossGoon.DistributedCashbotBossGoon):
            obj.d_requestWalk()
            obj.setObjectState('W', 0, obj.craneId)  # wake goon up