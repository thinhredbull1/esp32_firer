import struct

# raw data từ ESP8266
data = bytes([86, 88, 229, 76, 109, 145, 227, 47])

# unpack theo little-endian
lin_little = struct.unpack('<f', data[:4])[0]
ang_little = struct.unpack('<f', data[4:])[0]

# unpack theo big-endian
lin_big = struct.unpack('>f', data[:4])[0]
ang_big = struct.unpack('>f', data[4:])[0]

print("Little-endian:")
print("Linear:", lin_little)
print("Angular:", ang_little)

print("Big-endian:")
print("Linear:", lin_big)
print("Angular:", ang_big)
target=60
speed_init=200
for i in range(0,10):
   
    speed_new=speed_init*0.7+target*0.3
    speed_init=speed_new
    print(speed_new)