import socket
from typing import Optional, Sequence

from src.card import Card
from src.msg import *


class MainPlayer:
    def __init__(self, connection: socket.socket):
        self.playersOverAll: list[int] = []  # 记录所有玩家的手牌数, 包括自己, 每个 int 的索引值即为玩家序号
        self.connection = connection
        self.index = -1
        self.ownedCards: list[int] = []
        self._buf: bytes = b''

    def _sendMsg(self, code: bytes, content: Optional[str] = None):
        """
        向服务器发送一条消息
        :param code: 消息代码, 为一个字节长的 bytes, 是 msg.py 内的一个常量
        :param content: 消息内容, None 则不带内容
        """
        data = code + f"{content if content else ''}".encode() + b'\n'
        self.connection.sendall(data)

    def queryCards(self):
        """
        发送查询手牌的请求
        """
        self._sendMsg(MSG_QUERY_CARDS)

    def syncGameInfo(self):
        """
        发送同步服务端信息的请求
        """
        self._sendMsg(MSG_SYNC_GAME_INFO)

    def placeCard(self, cardIndexInHand: int, changeColor: Optional[int] = None):
        """
        发送出牌请求
        :param cardIndexInHand: 出的牌在手牌内的索引
        :param changeColor: 若为 变色牌 或 +4牌 则需要提供要改变成的颜色，常量见 Card 类
        """
        self._sendMsg(MSG_PLACE_CARD,
                      f'{self.ownedCards[cardIndexInHand]:03d}{changeColor if (changeColor is not None) else ""}')

    def uno(self):
        """
        发送UNO请求
        """
        self._sendMsg(MSG_UNO)

    def doubt(self, playerIndex: int):
        """
        发送质疑玩家未UNO的请求
        :param playerIndex: 要质疑的玩家序号
        """
        self._sendMsg(MSG_DOUBT, f"{playerIndex}")

    def passPlacing(self):
        """
        发送过牌请求
        """
        self._sendMsg(MSG_PASS)

    def readMsg(self) -> tuple[int, bytes]:
        """
        从服务端读取一条消息, 内容不含回车符
        :return: [消息码, 原消息内容]
        """
        get = self.connection.recv(1024)
        self._buf += get
        while b'\n' not in self._buf:
            self._buf += self.connection.recv(1024)
        ret, self._buf = self._buf.split(b'\n', 1)
        return ret[0], ret[1:]

    def loadCards(self, rawMsg: bytes):
        """
        将卡牌加载到手牌中
        :param rawMsg: MSG_QUERY_CARDS_RESULT 对应的原消息
        :return:
        """
        self.ownedCards.clear()
        while rawMsg:
            self.ownedCards.append(int(rawMsg[:3]))
            rawMsg = rawMsg[3:] if len(rawMsg) > 3 else b""

    def updateOverall(self, cutMsg: bytes):
        """
        更新玩家手牌数总览
        :param cutMsg: MSG_SYNC_GAME_INFO_RESULT 对应原消息的卡牌数部分
        :return:
        """
        self.playersOverAll.clear()
        while cutMsg:
            self.playersOverAll.append(int(cutMsg[:3]))
            cutMsg = cutMsg[3:] if len(cutMsg) > 3 else None

    def handleInput(self):
        """
        处理本机玩家在命令行的输入
        """
        while True:
            get = input("你的回合, 请输入你的操作 (输入 help 查询可用命令):")
            if get == "help":
                print("[pc 数字]:出牌, 数字处填写要出的牌在你手牌的索引")
                print("[doubt 数字]:质疑玩家未UNO, 数字处填写要质疑的玩家序号")
                print("[uno]:宣言UNO")
                print("[pass]:过牌")
            elif get.startswith("pc"):
                cardInHandIndex = int(get.split()[1])
                cardIndex = self.ownedCards[cardInHandIndex]
                card = Card.cardLib[cardIndex]
                if card.color == 4:  # 万能牌
                    get = input("输入你想转变的颜色(r/g/b/y):")
                    while get not in "rgby" or len(get) != 1:
                        get = input("无效颜色, 请重新输入(r/g/b/y):")
                    color = {'r': 0, 'g': 1, 'b': 2, 'y': 3}[get]
                    self.placeCard(cardInHandIndex, color)
                else:
                    self.placeCard(cardInHandIndex)
                break
            elif get.startswith("doubt"):
                playerIndex = int(get.split()[1])
                self.doubt(playerIndex)
                break
            elif get == "uno":
                self.uno()
                break
            elif get == "pass":
                self.passPlacing()
                break
