# Read Temperature & Humidity with DHT22
# Import Library
from machine import Pin  
from dht import DHT22
from time import sleep, ticks_ms
# Pin Setup
dht = DHT22(Pin(4))
i = 0
while True : 
  time = ticks_ms() / 1000
  i += 1
  try : 
    # Measure the temperature & humidity
    if(i == 3) : raise OSError('Test sensor failure') #<------- Try uncomment 2 of this if you wnat to try fail case
    dht.measure()
    
    # Retrieve the sensor's temperature and humidity values.
    temperature = dht.temperature()
    humidity = dht.humidity()
    
    # Show values to shell
    print('Attemp: ',i)
    print('Temperature:',temperature, 'Time',time)
    print('Humidity:',humidity, 'Time:',time)
  except OSError as error: 
    print('Attemp: ',i)
    print('ERROR: Sensor read failed', error, 'Time',time)
  # Delay 5 sec
  sleep(5)
