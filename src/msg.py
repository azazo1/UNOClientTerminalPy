_i = 1


def _nextChar() -> bytes:
    global _i
    _i += 1
    return asChar(_i - 1)


def asChar(src: int):
    return eval("b'\\x" + f"{src:02x}" + "'")  # 转换为一个字符


MSG_PLACE_CARD = _nextChar()  # 玩家请求出牌, content 为想要发出牌的序号(len:3, 不足三位用零补充), 在出 变色 和 +4 牌时还会追加颜色标记(len:1)
MSG_INVALID_ARGUMENT = _nextChar()  # 无效的沟通参数, 无 content
MSG_QUERY_CARDS = _nextChar()  # 玩家查询手牌, 无 content
MSG_QUERY_CARDS_RESULT = _nextChar()  # 玩家查询自己手牌内容的回复, content 为手牌卡牌序号(每个序号三个字符)连接而成
MSG_PLAYER_PLACE_CARD = _nextChar()  # 服务器广播玩家发牌, content 为玩家序号(len:1)和发出卡牌的序号(len:3)
MSG_CARD_NOT_IN_YOUR_HAND = _nextChar()  # 该卡牌不在该玩家手牌中, 无 content
MSG_SYNC_GAME_INFO = _nextChar()  # 查询游戏信息, 无 content
MSG_SYNC_GAME_INFO_RESULT = _nextChar()  # 游戏信息同步消息回复, content 为 发送玩家数(len:1), 查询者自身的玩家序号(len:1), 各个玩家的手牌数(len:玩家数*3)，当前回合玩家序号(len:1)，弃牌堆顶层的牌号(len:3)
MSG_CARD_CANNOT_BE_PLACE = _nextChar()  # 该卡牌不符合发出条件, 不含 content
_nextChar()  # 跳过回车符
MSG_REVERT = _nextChar()  # REVERT 牌被打出, content 为改变后的方向(正方向为1, 反方向为0)
MSG_PLUS2 = _nextChar()  # PLUS2 牌被打出, content 为被起作用的玩家序号(len:1), 两个被抽到的牌号(len:2*3) 非该玩家的客户端应忽略该牌号
MSG_PLUS4 = _nextChar()  # PLUS4 牌被打出, content 为被加四张牌的玩家序号(len:1), 被加上的牌的牌号(len4*3) 非该玩家的客户端应忽略牌号
MSG_CHANGE_COLOR = _nextChar()  # CHANGE_COLOR 牌被打出, content 为新的可用颜色(len:1)
MSG_PASS = _nextChar()  # 玩家选择不出牌, 过牌, 无 content
MSG_PLAYER_PASSED = _nextChar()  # 服务器广播玩家过牌, content 为过牌玩家序号(len:1), 玩家抽取的两张牌(len:2*3)
MSG_GAME_OVER = _nextChar()  # 游戏结束, content 为每位玩家的得分(len:5)连接，按玩家序号排序
MSG_DOUBT = _nextChar()  # 某位玩家质疑另一位玩家没有宣言 UNO, content 为被质疑的玩家
MSG_PLAYER_DOUBTED = _nextChar()  # 服务器广播某位玩家质疑另外一位玩家, content 为是否质疑成功(len:1), 质疑者(len:1), 被质疑者(len:1), 若质疑成功则追加两张牌的牌号(len:2*3), 非被质疑玩家的客户端应忽略此牌号
MSG_UNO = _nextChar()  # 玩家宣布 UNO, 无 content
MSG_PLAYER_UNOED = _nextChar()  # 服务器广播玩家uno, content 为uno玩家的序号(len:1)
MSG_UNO_FAILED = _nextChar()  # 服务器通知尝试UNO的玩家UNO失败, 无 content
MSG_GAME_START = _nextChar()  # 服务器广播游戏开始, 无 content
MSG_GAME_OVER_WITH_EXCEPTION = _nextChar()  # 服务器广播游戏异常结束, 无 content
MSG_ITS_YOUR_TURN = _nextChar()  # 服务器通知玩家到他的回合, 无 content
MSG_BAN_PLAYER = _nextChar()  # 玩家被BAN卡封禁, content 为被封禁玩家的序号(len:1)
MSG_GAME_OVER_WITH_CARDLIB_EXHAUSTED = _nextChar()  # 牌库不足并结束游戏, content 为每位玩家的得分(len:5)连接，按玩家序号排序
MSG_NOT_YOUR_TURN = _nextChar()  # 服务器通知玩家在非他回合发出了出牌/质疑/UNO请求, 无 content
