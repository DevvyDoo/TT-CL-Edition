from otp.ai.AIBaseGlobal import *
from direct.distributed.ClockDelta import *
import DistributedBossCogAI
from direct.directnotify import DirectNotifyGlobal
from otp.avatar import DistributedAvatarAI
import DistributedSuitAI
from toontown.battle import BattleExperienceAI
from direct.fsm import FSM
from toontown.toonbase import ToontownGlobals
from toontown.toon import InventoryBase
from toontown.toonbase import TTLocalizer
from toontown.battle import BattleBase
from toontown.toon import NPCToons
from toontown.suit import SellbotBossGlobals
import SuitDNA, random

class DistributedSellbotBossAI(DistributedBossCogAI.DistributedBossCogAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSellbotBossAI')
    limitHitCount = 6
    numPies = ToontownGlobals.FullPies

    def __init__(self, air):
        DistributedBossCogAI.DistributedBossCogAI.__init__(self, air, 's')
        FSM.FSM.__init__(self, 'DistributedSellbotBossAI')
        self.doobers = []
        self.bossMaxDamage = ToontownGlobals.SellbotBossMaxDamage
        self.pieHitToonup = SellbotBossGlobals.PieToonup
        self.pieDamageMult = SellbotBossGlobals.PieDamageMult
        self.hitCountDamage = SellbotBossGlobals.HitCountDamage
        self.recoverRate = 0
        self.recoverStartTime = 0

    def generateWithRequired(self, zoneId):
        self.__setCagedToonNpcId()
        DistributedBossCogAI.DistributedBossCogAI.generateWithRequired(self, zoneId)

    def delete(self):
        self.destroyEasyModeBarrels()
        return DistributedBossCogAI.DistributedBossCogAI.delete(self)

    def getHoodId(self):
        return ToontownGlobals.SellbotHQ

    def getCagedToonNpcId(self):
        self.cagedToonNpcId = random.choice(NPCToons.npcFriendsMinMaxStars(3, 5))
        return self.cagedToonNpcId

    def __setCagedToonNpcId(self):
        self.cagedToonNpcId = random.choice(NPCToons.npcFriendsMinMaxStars(3, 5))

    def magicWordHit(self, damage, avId):
        if self.attackCode != ToontownGlobals.BossCogDizzyNow:
            self.hitBossInsides()
        self.hitBoss(damage)

    def hitBoss(self, bossDamage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'DistributedSellbotBossAI.hitBoss from unknown avatar'):
            return
        self.validate(avId, bossDamage == 1, 'invalid bossDamage %s' % bossDamage)
        bossDamage = int(round(bossDamage * self.pieDamageMult))
        if bossDamage < 1:
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BossRound':
            return
        if self.attackCode != ToontownGlobals.BossCogDizzyNow:
            return
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.b_setBossDamage(bossDamage, 0, 0)
        if self.bossDamage >= self.bossMaxDamage:
            self.setState('NearVictory')
        else:
            self.__recordHit()

    def hitBossInsides(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'hitBossInsides from unknown avatar'):
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BossRound':
            return
        self.b_setAttackCode(ToontownGlobals.BossCogDizzyNow)
        self.b_setBossDamage(self.getBossDamage(), 0, 0)

    def hitToon(self, toonId):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId != toonId, 'hitToon on self'):
            return
        if avId not in self.involvedToons or toonId not in self.involvedToons:
            return
        toon = self.air.doId2do.get(toonId)
        if toon:
            self.healToon(toon, self.pieHitToonup)

    def getDamageMultiplier(self):
        return SellbotBossGlobals.AttackMult

    def touchCage(self):
        avId = self.air.getAvatarIdFromSender()
        currState = self.getCurrentOrNextState()
        if currState != 'BossRound' and currState != 'NearVictory':
            return
        if not self.validate(avId, avId in self.involvedToons, 'touchCage from unknown avatar'):
            return
        toon = simbase.air.doId2do.get(avId)
        if toon:
            toon.b_setNumPies(self.numPies)
            toon.__touchedCage = 1
            self.__goodJump(avId)

    def finalPieSplat(self):
        if self.state != 'NearVictory':
            return
        self.b_setState('Victory')

    def doNextAttack(self, task):
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            attackCode = ToontownGlobals.BossCogRecoverDizzyAttack
        else:
            attackCode = random.choice([ToontownGlobals.BossCogAreaAttack, ToontownGlobals.BossCogFrontAttack, ToontownGlobals.BossCogDirectedAttack, ToontownGlobals.BossCogDirectedAttack, ToontownGlobals.BossCogDirectedAttack, ToontownGlobals.BossCogDirectedAttack])
        if attackCode == ToontownGlobals.BossCogAreaAttack:
            self.__doAreaAttack()
        else:
            if attackCode == ToontownGlobals.BossCogDirectedAttack:
                self.__doDirectedAttack()
            else:
                self.b_setAttackCode(attackCode)

    def __doAreaAttack(self):
        self.b_setAttackCode(ToontownGlobals.BossCogAreaAttack)
        if self.recoverRate:
            newRecoverRate = min(200, self.recoverRate * 1.2)
        else:
            newRecoverRate = 2
        now = globalClock.getFrameTime()
        self.b_setBossDamage(self.getBossDamage(), newRecoverRate, now)

    def __doDirectedAttack(self):
        if self.nearToons:
            toonId = random.choice(self.nearToons)
            self.b_setAttackCode(ToontownGlobals.BossCogDirectedAttack, toonId)
        else:
            self.__doAreaAttack()

    def b_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.d_setBossDamage(bossDamage, recoverRate, recoverStartTime)
        self.setBossDamage(bossDamage, recoverRate, recoverStartTime)

    def setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.bossDamage = bossDamage
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime

    def getBossDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime
        return int(max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0))

    def d_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        timestamp = globalClockDelta.localToNetworkTime(recoverStartTime)
        self.sendUpdate('setBossDamage', [bossDamage, recoverRate, timestamp])

    def waitForNextStrafe(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BossRound':
            taskName = self.uniqueName('NextStrafe')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextStrafe, taskName)

    def stopStrafes(self):
        taskName = self.uniqueName('NextStrafe')
        taskMgr.remove(taskName)

    def doNextStrafe(self, task):
        if self.attackCode != ToontownGlobals.BossCogDizzyNow:
            side = random.choice([0, 1])
            direction = random.choice([0, 1])
            self.sendUpdate('doStrafe', [side, direction])
        delayTime = 9
        self.waitForNextStrafe(delayTime)

    def __sendDooberIds(self):
        dooberIds = []
        for suit in self.doobers:
            dooberIds.append(suit.doId)

        self.sendUpdate('setDooberIds', [dooberIds])

    def d_cagedToonBossRound(self, index, avId):
        #self.sendUpdate('CagedToonBattleThree', [index, avId])
        pass

    def formatReward(self):
        return str(self.cagedToonNpcId)

    def makeBattleOneBattles(self):
        self.postBattleState = 'RollToBattleTwo'
        self.initializeBattles(1, ToontownGlobals.SellbotBossBattleOnePosHpr)

    def generateSuits(self, battleNumber):
        if self.nerfed:
            if battleNumber == 1:
                return self.invokeSuitPlanner(15, 0)
            else:
                return self.invokeSuitPlanner(16, 1)
        else:
            if battleNumber == 1:
                return self.invokeSuitPlanner(9, 0)
            else:
                return self.invokeSuitPlanner(10, 1)

    def removeToon(self, avId, died=False):
        toon = simbase.air.doId2do.get(avId)
        if toon:
            toon.b_setNumPies(0)
        DistributedBossCogAI.DistributedBossCogAI.removeToon(self, avId, died=died)

    def enterOff(self):
        DistributedBossCogAI.DistributedBossCogAI.enterOff(self)
        self.__resetDoobers()

    def enterElevator(self):
        DistributedBossCogAI.DistributedBossCogAI.enterElevator(self)
        self.b_setBossDamage(0, 0, 0)

    def enterIntroduction(self):
        DistributedBossCogAI.DistributedBossCogAI.enterIntroduction(self)
        self.__makeDoobers()
        self.b_setBossDamage(0, 0, 0)

    def exitIntroduction(self):
        DistributedBossCogAI.DistributedBossCogAI.exitIntroduction(self)
        self.__resetDoobers()

    def enterPrepareBossRound(self):
        self.barrier = self.beginBarrier('PrepareBossRound', self.involvedToons, 30, self.__donePrepareBossRound)

    def __donePrepareBossRound(self, avIds):
        self.b_setState('BossRound')

    def exitPrepareBossRound(self):
        self.ignoreBarrier(self.barrier)

    def enterBossRound(self):
        self.setPieType()
        self.b_setBossDamage(0, 0, 0)
        self.BossRoundStart = globalClock.getFrameTime()
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.__touchedCage = 0

        self.waitForNextAttack(5)
        self.waitForNextStrafe(9)
        self.cagedToonDialogIndex = 100
        self.__saySomethingLater()

    def __saySomething(self, task=None):
        index = None
        avId = 0
        if len(self.involvedToons) == 0:
            return
        avId = random.choice(self.involvedToons)
        toon = simbase.air.doId2do.get(avId)
        if toon.__touchedCage:
            if self.cagedToonDialogIndex <= TTLocalizer.CagedToonBattleThreeMaxAdvice:
                index = self.cagedToonDialogIndex
                self.cagedToonDialogIndex += 1
            elif random.random() < 0.2:
                index = random.randrange(100, TTLocalizer.CagedToonBattleThreeMaxAdvice + 1)
        else:
            index = random.randrange(20, TTLocalizer.CagedToonBattleThreeMaxTouchCage + 1)
        if index:
            self.d_cagedToonBossRound(index, avId)
        self.__saySomethingLater()
        return

    def __saySomethingLater(self, delayTime=15):
        taskName = self.uniqueName('CagedToonSaySomething')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.__saySomething, taskName)

    def __goodJump(self, avId):
        currState = self.getCurrentOrNextState()
        if currState != 'BossRound':
            return
        index = random.randrange(10, TTLocalizer.CagedToonBattleThreeMaxGivePies + 1)
        self.d_cagedToonBossRound(index, avId)
        self.__saySomethingLater()

    def exitBossRound(self):
        self.stopAttacks()
        self.stopStrafes()
        taskName = self.uniqueName('CagedToonSaySomething')
        taskMgr.remove(taskName)

    def enterNearVictory(self):
        #Whisper out the time from the start of VP until end of VP
        self.pieTime = globalClock.getFrameTime()
        for doId, do in simbase.air.doId2do.items():
            if str(doId)[0] != str(simbase.air.districtId)[0]:
                do.d_setSystemMessage(0, "Crane Round Ended In {0:.5f}s".format(self.pieTime - self.BossRoundStart))

    def exitNearVictory(self):
        pass

    def enterVictory(self):
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 10, self.__doneVictory)
        return

    def __doneVictory(self, avIds):
        self.b_setState('Reward')

    def __shouldPromoteToon(self, toon):
        if not toon.readyForPromotion(self.deptIndex):
            return False
        else:
            if self.isToonWearingRentalSuit(toon.doId):
                return False
        return True

    def exitVictory(self):
        self.takeAwayPies()

    def enterFrolic(self):
        DistributedBossCogAI.DistributedBossCogAI.enterFrolic(self)
        self.b_setBossDamage(0, 0, 0)

    def __resetDoobers(self):
        for suit in self.doobers:
            suit.requestDelete()

        self.doobers = []

    def __makeDoobers(self):
        self.__resetDoobers()
        for i in xrange(8):
            suit = DistributedSuitAI.DistributedSuitAI(self.air, None)
            level = random.randrange(len(SuitDNA.suitsPerLevel))
            suit.dna = SuitDNA.SuitDNA()
            suit.dna.newSuitRandom(level=level, dept=self.dna.dept)
            suit.setLevel(level)
            suit.generateWithRequired(self.zoneId)
            self.doobers.append(suit)

        self.__sendDooberIds()
        return

    def setPieType(self):
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.d_setPieType(4)

    def takeAwayPies(self):
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.b_setNumPies(0)

    def __recordHit(self):
        now = globalClock.getFrameTime()
        self.hitCount += 1
        if self.hitCount < self.limitHitCount or self.bossDamage < self.hitCountDamage:
            return
        self.b_setAttackCode(ToontownGlobals.BossCogRecoverDizzyAttack)

    def createEasyModeBarrels(self):
        self.barrels = []
        for entId, entDef in SellbotBossGlobals.BarrelDefs.iteritems():
            barrelType = entDef['type']
            barrel = barrelType(self.air, entId)
            SellbotBossGlobals.setBarrelAttr(barrel, entId)
            barrel.generateWithRequired(self.zoneId)
            self.barrels.append(barrel)

    def destroyEasyModeBarrels(self):
        if hasattr(self, 'barrels') and self.barrels:
            for barrel in self.barrels:
                barrel.requestDelete()

            self.barrels = []
