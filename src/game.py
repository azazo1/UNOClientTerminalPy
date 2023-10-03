import socket

from src.card import Card
from src.msg import *

from src import card
from src.player import MainPlayer


class Game:
    def __init__(self, serverIP: str, serverPort: int):
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.mainPlayer: MainPlayer = None
        self.playerNumber = -1
        self.topOfThrownCard = -1
        self.currentPlayerIndex = -1
        self.running = True
        self.postHandleInputAfterGameInfo = True  # 用于在获取游戏消息后获取用户输入

    def gameLoop(self):
        card.Card.initCardLib()
        connection = socket.socket()
        connection.connect((self.serverIP, self.serverPort))
        print("->连接到游戏")
        self.mainPlayer = MainPlayer(connection)
        while self.running:
            msgCode, rawMsg = self.mainPlayer.readMsg()
            self.handleMsg(msgCode, rawMsg)

    def handleMsg(self, msgCode: int, rawMsg: bytes):
        msgCodeChar = asChar(msgCode)
        if msgCodeChar == MSG_GAME_START:
            # 同步消息
            self.mainPlayer.queryCards()
            self.mainPlayer.syncGameInfo()
        elif msgCodeChar == MSG_QUERY_CARDS_RESULT:
            self.mainPlayer.loadCards(rawMsg)
        elif msgCodeChar == MSG_SYNC_GAME_INFO_RESULT:
            self.playerNumber = int(chr(rawMsg[0]))
            self.mainPlayer.index = int(chr(rawMsg[1]))
            self.mainPlayer.updateOverall(rawMsg[2:2 + self.playerNumber * 3])
            cutMsg = rawMsg[2 + self.playerNumber * 3:]
            self.currentPlayerIndex = int(chr(cutMsg[0]))
            self.topOfThrownCard = int(cutMsg[1:])
            print(f"--你是玩家 {self.mainPlayer.index}, \n"
                  f"--你的剩余手牌为: {[str(Card.cardLib[i]) for i in self.mainPlayer.ownedCards]}, \n"
                  f"--现在场上玩家剩余手牌数为: {self.mainPlayer.playersOverAll}, \n"
                  f"--轮到玩家 {self.currentPlayerIndex} 操作")
            if self.postHandleInputAfterGameInfo and self.currentPlayerIndex == self.mainPlayer.index:
                self.mainPlayer.handleInput()
                self.postHandleInputAfterGameInfo = False
        elif msgCodeChar == MSG_NOT_YOUR_TURN:
            print("xx不是你的回合, 操作失败")
        elif msgCodeChar == MSG_INVALID_ARGUMENT:
            print("xx参数无效")
            self.mainPlayer.handleInput()
        elif msgCodeChar == MSG_CARD_NOT_IN_YOUR_HAND:
            print("xx你手上没有这张牌")
            self.mainPlayer.handleInput()
        elif msgCodeChar == MSG_CARD_CANNOT_BE_PLACE:
            print("xx该牌不符合打出要求")
            self.mainPlayer.handleInput()
        elif msgCodeChar == MSG_PLAYER_PLACE_CARD:
            playerIndex = int(chr(rawMsg[0]))
            placedCardIndex = int(rawMsg[1:])
            print(f"**玩家 {playerIndex} 打出了牌 {str(Card.cardLib[placedCardIndex])}")
        elif msgCodeChar == MSG_BAN_PLAYER:
            playerIndex = int(chr(rawMsg[0]))
            if playerIndex == self.mainPlayer.index:
                print("!!你被禁止牌封禁了")
            else:
                print(f"--玩家 {playerIndex} 被禁止牌封禁了")
        elif msgCodeChar == MSG_REVERT:
            direction = rawMsg[0] == b'1'
            print(f"*>反转牌发动, 现在{'正' if direction else '反'}向进行")
        elif msgCodeChar == MSG_PLUS2:
            playerIndex = int(chr(rawMsg[0]))
            card1Index = int(rawMsg[1:4])
            card2Index = int(rawMsg[4:7])
            if playerIndex == self.mainPlayer.index:
                print(f"*>+2牌发动, 你被禁止出牌, 并强制抽取牌: {Card.cardLib[card1Index]} {Card.cardLib[card2Index]}")
            else:
                print(f"*>+2牌发动, 玩家 {playerIndex} 被禁止出牌, 并强制抽取2张牌")
        elif msgCodeChar == MSG_PLUS4:
            playerIndex = int(chr(rawMsg[0]))
            color = int(chr(rawMsg[1]))
            card1Index = int(rawMsg[2:5])
            card2Index = int(rawMsg[5:8])
            card3Index = int(rawMsg[8:11])
            card4Index = int(rawMsg[11:14])
            if playerIndex == self.mainPlayer.index:
                print(
                    f"*>+4牌发动, 颜色转换为 {Card.colorCast[color]}, 出牌者继续出牌, 你被强制抽取牌: {Card.cardLib[card1Index]} {Card.cardLib[card2Index]} {Card.cardLib[card3Index]} {Card.cardLib[card4Index]}")
            else:
                print(
                    f"*>+4牌发动, 颜色转换为 {Card.colorCast[color]}, 出牌者继续出牌, 玩家 {playerIndex} 被强制抽取4张牌")
        elif msgCodeChar == MSG_CHANGE_COLOR:
            color = int(chr(rawMsg[0]))
            print(f"->变色牌打出, 变成{Card.colorCast[color]}色")
        elif msgCodeChar == MSG_PLAYER_PASSED:
            playerIndex = int(chr(rawMsg[0]))
            if playerIndex != self.mainPlayer.index:
                print(f"--玩家 {playerIndex} 选择过牌, 并抽取两张牌")
            else:
                cardIndex1 = int(rawMsg[1:4])
                cardIndex2 = int(rawMsg[4:7])
                print(f"--你选择过牌, 并抽取两张牌: {Card.cardLib[cardIndex1]} {Card.cardLib[cardIndex2]}")
        elif msgCodeChar == MSG_GAME_OVER:
            scores: list[tuple[int, int]] = []
            for i in range(self.playerNumber):
                scores.append((i, int(rawMsg[i * 5:i * 5 + 5])))
            scores = sorted(scores, key=lambda ele: ele[1])
            print(f"->玩家 {scores[0][0]} 手牌打完, 游戏结束, 分数(越小排名越高):")
            for item in scores:
                print(f"->    玩家 {item[0]}: {item[1]} 分")
            self.running = False
        elif msgCodeChar == MSG_PLAYER_DOUBTED:
            success = int(chr(rawMsg[0]))
            playerIndex = int(chr(rawMsg[1]))
            doubtedPlayerIndex = int(chr(rawMsg[2]))
            if success:
                if doubtedPlayerIndex == self.mainPlayer.index:
                    card1Index = rawMsg[3:6]
                    card2Index = rawMsg[6:9]
                    print(
                        f"!!你被玩家 {playerIndex} 质疑未宣言UNO, 惩罚两张牌: {Card.cardLib[card1Index]} {Card.cardLib[card2Index]}")
                else:
                    print(f"!!玩家 {doubtedPlayerIndex} 被质疑未宣言UNO, 惩罚两张牌")
            else:
                print(f"!!玩家 {playerIndex} 尝试质疑玩家 {doubtedPlayerIndex} 未宣言UNO, 但质疑失败")
            if playerIndex == self.mainPlayer.index:
                self.mainPlayer.handleInput()
        elif msgCodeChar == MSG_UNO_FAILED:
            print("!!宣言UNO失败")
            self.mainPlayer.handleInput()
        elif msgCodeChar == MSG_PLAYER_UNOED:
            playerIndex = int(chr(rawMsg[0]))
            print(f"!!玩家 {playerIndex} 宣言UNO")
            if playerIndex == self.mainPlayer.index:
                self.mainPlayer.handleInput()
        elif msgCodeChar == MSG_GAME_OVER_WITH_EXCEPTION:
            print("->游戏异常退出")
            self.running = False
        elif msgCodeChar == MSG_ITS_YOUR_TURN:
            self.mainPlayer.queryCards()
            self.mainPlayer.syncGameInfo()
            self.postHandleInputAfterGameInfo = True
        elif msgCodeChar == MSG_GAME_OVER_WITH_CARDLIB_EXHAUSTED:
            scores: list[tuple[int, int]] = []
            for i in range(self.playerNumber):
                scores.append((i, int(rawMsg[i * 5:i * 5 + 5])))
            scores = sorted(scores, key=lambda ele: ele[1])
            print("->牌库耗尽, 游戏结束, 分数(越小排名越高):")
            for item in scores:
                print(f"->    玩家 {item[0]}: {item[1]} 分")
            self.running = False
        # print(msgCode, rawMsg)
