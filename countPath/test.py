import serial, binascii, time

COM_PORT  = '/dev/ttyUSB0'
BAUD_RATE = 57600

ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(1)  # 等模組啟動

try:
    while True:
        # 改成每次讀 128 bytes，並拿掉 flushInput()
        data = ser.read(128)
        if not data:
            continue

        hexstr = binascii.hexlify(data).decode()
        print(hexstr)         # 印出整串 hex
        print('-'*60)         # 分隔線
        time.sleep(0.5)

except KeyboardInterrupt:
    ser.close()
