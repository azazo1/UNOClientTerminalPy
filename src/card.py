class Card:
    cardLib = []
    signalCast = ['数字0', '数字1', '数字2', '数字3', '数字4', '数字5', '数字6', '数字7', '数字8', '数字9', '禁止',
                  '反转', '+2', '变色', '+4']
    colorCast = ['红', '绿', '蓝', '黄', '万能色']

    def __init__(self, signal: int, color: int):
        self.signal = signal
        self.color = color

    def __str__(self):
        return self.signalCast[self.signal] + self.colorCast[self.color]

    @classmethod
    def initCardLib(cls):
        cls.cardLib.clear()
        for color in range(4):  # NUMBER_0 各色只有一张
            cls.cardLib.append(Card(0, color))
        for signal in range(1, 13):  # 13 和 14 号不用添加颜色单独讨论
            for color in range(4):  # 四种颜色
                for _ in range(2):  # 各色两张
                    cls.cardLib.append(Card(signal, color))
        for signal in range(13, 15):
            for _ in range(4):
                cls.cardLib.append(Card(signal, 4))
