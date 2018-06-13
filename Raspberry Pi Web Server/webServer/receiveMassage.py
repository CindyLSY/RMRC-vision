import smbus

bus = smbus.SMBus(1)

def request_reading():
	reading = int(bus.read_byte(0x04))
	print(reading)

request_reading();