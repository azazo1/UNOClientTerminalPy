from src.game import Game

if __name__ == '__main__':
    # ip, port = input("输入服务器地址:").split(":")
    ip, port = "127.0.0.1", 12345
    port = int(port)
    Game(ip, port).gameLoop()
    input("回车退出")
