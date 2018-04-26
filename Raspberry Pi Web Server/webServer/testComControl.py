import smbus                #I2C通信するためのモジュールsmbusをインポートする
import time                 #sleepするためにtimeモジュールをインポートする

"""メイン関数"""
if __name__ == '__main__':
    bus = smbus.SMBus(1)    ##I2C通信するためのモジュールsmbusのインスタンスを作成
    adress = 0x04           #arduinoのサンプルプログラムで設定したI2Cチャンネル

    
    bus.write_byte(adress, ord('a'))
    time.sleep(0.01)
    
    bus.write_byte(adress, 129)

    time.sleep(1)
    bus.write_byte(adress, ord('c'))
    time.sleep(0.01)
    bus.write_byte(adress, 3)
    
    time.sleep(1)
    msg = chr(bus.read_byte(adress))
    print(msg)
    
    #stops program
    bus.write_byte(adress, 255)

    #0.5sスリープする
    time.sleep(1)

