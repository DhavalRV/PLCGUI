from plcLib import PLC
import time
p=PLC('10.40.0.2')
t=time.time()
while(1):
	s=p.readSensors()
	print(s)
	if(s[0]):
		print(time.time()-t)
		t=time.time()
		#