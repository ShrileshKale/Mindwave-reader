import smbus
bus = smbus.SMBus(1)

data = bus.read_i2c_block_data(0x33, 32)
arraySize = len(data)
print(arraySize)
num = 0
while(num != arraySize):
	
       print(data[num])
       num+= 1
           
  
