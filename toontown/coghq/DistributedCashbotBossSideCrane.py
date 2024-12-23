from direct.distributed.ClockDelta import *
from direct.fsm import FSM
from toontown.coghq import DistributedCashbotBossCrane
from toontown.coghq import DistributedCashbotBossSafe
from panda3d.core import *
from panda3d.direct import *
from panda3d.physics import *
from panda3d.core import LOrientationf
from direct.interval.IntervalGlobal import *
from direct.distributed import DistributedObject
from direct.showutil import Rope
from direct.showbase import PythonUtil
from direct.task import Task
from toontown.toonbase import ToontownGlobals

from toontown.suit import DistributedCashbotBossGoon
import random


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
        self.draggedObjects = []
        self.sniffing = False

    def getName(self):
        return 'SideCrane-%s' % self.index
        
    def dragObject(self, obj, task=None):
        """Continuously apply drag force while in Dragged state"""

        if (self.state == 'Off' or not self.magnetOn) and not self.sniffing:
            self.releaseObject(safe=obj)
            return Task.done
        
        if obj not in self.draggedObjects:
            return Task.done
        
        # Apply the same force logic as dropObject
        if obj.lerpInterval:
            obj.lerpInterval.finish()

        obj.wrtReparentTo(render)
        obj.lerpInterval = Parallel(obj.quatInterval(ToontownGlobals.CashbotBossFromMagnetTime, VBase3(obj.getH(), 0, 0), blendType='easeOut'))
        obj.lerpInterval.start()
        
        p1 = self.bottomLink.node().getPhysicsObject()
        v = render.getRelativeVector(self.bottomLink, p1.getVelocity())
        obj.physicsObject.setVelocity(v)
        
        return Task.cont

    def getPointsForStun(self):
        return self.boss.ruleset.POINTS_SIDESTUN

    # Override base method, always wake up goons
    def considerObjectState(self, obj):
        if isinstance(obj, DistributedCashbotBossGoon.DistributedCashbotBossGoon):
            obj.d_requestWalk()
            obj.setObjectState('W', 0, obj.craneId)  # wake goon up

    # Override base method, account for Dragged safes
    def releaseObject(self, safe=None):
        # Don't confuse this method with dropObject.  That method
        # implements the object's request to move out of the Grabbed
        # state, and is called only by the object itself, while
        # releaseObject() is called by the crane and asks the object
        # to drop itself, so that the object will set its state
        # appropriately.  A side-effect of this call will be an
        # eventual call to dropObject() by the newly-released object.

        if self.boss:
            self.boss.craneStatesDebug(doId=self.doId,
                                   content='pre-Releasing object, currently holding: %s' % (self.heldObject.getName() if self.heldObject else "Nothing"))
        
        if self.heldObject:
            obj = self.heldObject
            obj.d_requestDrop()
            if (obj.state == 'Grabbed' or obj.state == 'LocalGrabbed'):
                # Go ahead and move the local object instance into the
                # 'LocalDropped' state--presumably the AI will grant our
                # request shortly anyway, and we can avoid a hitch by
                # not waiting around for it.  However, we can't do
                # this if the object is just in 'LocalGrabbed' state,
                # because we can't start broadcasting updates on the
                # object's position until we *know* we're the object's
                # owner.
                obj.demand('LocalDropped', localAvatar.doId, self.doId)

        elif safe and safe in self.draggedObjects:
            obj = safe
            obj.d_requestDrop()

        if self.boss:
            self.boss.craneStatesDebug(doId=self.doId,
                                   content='post-Releasing object, currently holding: %s' % (self.heldObject.getName() if self.heldObject else "Nothing"))

    # Override base method, drop the object when no longer sniffing
    def sniffedNothing(self, entry):
        self.sniffing = False
        # Something was sniffed as grabbable.
        np = entry.getIntoNodePath()
        
        if np.hasNetTag('object'):
            doId = int(np.getNetTag('object'))
        else:
            self.notify.warning("%s missing 'object' tag" % np)
            return
            
        self.notify.debug('sniffedNothing %d' % doId)

        obj = base.cr.doId2do.get(doId)

        if obj in self.draggedObjects:
            self.releaseObject(safe=obj)
        pass

    # Override base method, sniff something functions differently
    # drag safes instead of grab
    def sniffedSomething(self, entry):
        self.sniffing = True
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
                if obj.state != 'Dragged':
                    obj.d_requestDrag()
                return
            
            self.considerObjectState(obj)
            obj.d_requestGrab()
            obj.demand('LocalGrabbed', localAvatar.doId, self.doId)