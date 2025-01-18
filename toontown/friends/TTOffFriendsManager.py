import json

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal

import base64


class TTOffFriendsManager(DistributedObjectGlobal):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTOffFriendsManager')

    def d_getAvatarDetails(self, avId):
        self.sendUpdate('getAvatarDetails', [avId])

    def avatarDetailsResp(self, avId, details):
        fields = json.loads(details)

        # The following fields were converted to a string to satisfy json.dumps() from UD and need conversion
        BYTE_FIELDS = ('setExperience', 'setDNAString', 'setInventory')

        for currentField in fields:
            fieldName: str = currentField[0]

            # If we have an encoded byte field, go back to what it was
            if fieldName in BYTE_FIELDS:
                currentField[1] = base64.b64decode(currentField[1])

        base.cr.handleGetAvatarDetailsResp(avId, fields=fields)

    def d_getFriendsListRequest(self):
        self.sendUpdate('getFriendsListRequest')

    def friendsListRequestResp(self, resp):
        base.cr.handleGetFriendsList(resp)

    def friendOnline(self, id, commonChatFlags, whitelistChatFlags, alert=True):
        base.cr.handleFriendOnline(id, commonChatFlags, whitelistChatFlags, alert)

    def d_removeFriend(self, friendId):
        self.sendUpdate('removeFriend', [friendId])

    def friendOffline(self, id):
        base.cr.handleFriendOffline(id)
