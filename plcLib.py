from pymodbus.client.sync import ModbusTcpClient
import time


GLOVE_PRESENT_ADDR=2048		#M0
RASM_ANCHOR_ADDR=2052  		#M4
PURGER_ADDR=2058			#M10
FORMER_ANCHOR_ADDR=2059  	#M11
PURGING_DURATION_ADDR=4096 	#D0
PURGE_INTERVAL_ADDR=4106	#D10
PURGE_DELAY_ADDR=4116		#D20
DUAL_BIN_FLAP_ON=2548			#M500
DUAL_BIN_FLAP_OFF=2598			#M550
FLIP_DURATION_ADDR=4146		#D50
FURS_ADDR=2748				#M700
FURS_ON_TIME=4166			#D70



###TODO: Handle Connection Failure Exception (wait to reconnect every minute )
class PLC():
	timeSpan=0
	connected=False
	prev_res=0
	def __init__(self, ip):
		#ip should be 10.3.0.2
		self.client = ModbusTcpClient(ip)
		self.connected = self.client.connect()
		self.clearFlags()
		#self.setDefaultPurgingTime()
	def changeIP(self, ip):
		if self.connected:
			self.client.close()
			print("Modbus TCP connection closed")
		self.client = ModbusTcpClient(ip)
		self.connected = self.client.connect()
		if self.connected:
			self.clearFlags()
		return self.connected

	def clearFlags(self):
		if self.connected:
			self.client.write_coils(GLOVE_PRESENT_ADDR, (0,0,0,0,0,0,0,0,0)) #Clear all flags
			self.client.write_register(FURS_ON_TIME,5)#half second


	def waitNextGloveFlicker(self):
		if self.connected:
			for i in range(50):
				result = self.client.read_discrete_inputs(GLOVE_PRESENT_ADDR,1)
				if(self.prev_res==0 and result.bits[0]>0): #Check for rising edge
					self.prev_res=result.registers[0]
					return 1
				self.prev_res=result.registers[0]
				time.sleep(0.02)
			print("Production Line Stopped")
			return 0
		print("No PLC Connection")
		time.sleep(0.5)
		#Do not wait next glove if no connection, return -1
		return -1

	def waitNextGlove(self):
		if self.connected:
			for i in range(500):
				if not self.connected:
					break
				try:
					result = self.client.read_discrete_inputs(GLOVE_PRESENT_ADDR,1)
					if result.bits[0]:
						self.client.write_coil(GLOVE_PRESENT_ADDR, False)
						time.sleep(0.03) ##Displacement delay
						return 1
					time.sleep(0.002)
				except:
					print("Changing PLC IP Address")
			print("Production Line Stopped")
			return 0
		time.sleep(1)
		print("No PLC Connection")
		#Do not wait next glove if no connection, return 0
		return -1
	def readSensors(self):
		if self.connected:
			try:
				result = self.client.read_discrete_inputs(GLOVE_PRESENT_ADDR,4)
				for side, bit in enumerate(result.bits):
					if bit:
						self.client.write_coil(GLOVE_PRESENT_ADDR+side, False)
				return result.bits
			except:
				print("Changing PLC IP Address")
		print("No PLC Connection")
		#Do not wait next glove if no connection, return 0
		return -1

	def purgeGlove32(self, line):
		if self.connected:
			#activate purger by setting M1, will be cleared by PLC
			self.client.write_register(PURGER_ADDR+line, 1)
			time.sleep(0.5)
			self.client.write_register(PURGER_ADDR+line, 0)

	def purgeGlove(self, line):
		if self.connected:
			#activate purger by setting M1, will be cleared by PLC
			self.client.write_coil(PURGER_ADDR+line, True)

	def setPurgeDelay_100ms(self,line,val):
		if self.connected:
			self.client.write_register(PURGE_DELAY_ADDR+line,val)

	def setPurgeDuration_100ms(self,line,val):
		if self.connected:
			self.client.write_register(PURGING_DURATION_ADDR+line,val)

	def setPurgeInterval_100ms(self,line,val):
		if self.connected:
			self.client.write_register(PURGE_INTERVAL_ADDR+line,val)

	def setDefaultPurgingTime(self):
		if self.connected:
			for i in range(4):
				self.setPurgeDuration_100ms(i,8)
				self.setPurgeInterval_100ms(i,3)

	def isFormerAnchor(self):
		return self.readNClearFlag(FORMER_ANCHOR_ADDR) #Former Anchor Flag M11

	def readRasmAnchor(self,side):
		return self.readNClearFlag(RASM_ANCHOR_ADDR+side) #RASM Anchor Flag M4~M7

	def readNClearFlag(self, addr):
		if self.connected:
			try:
				result = self.client.read_discrete_inputs(addr,1)
				if result.bits[0]:
					self.client.write_coil(addr, False)
					return 1	#read and cleared
				else:
					return 0	#no flag
			except AttributeError:
				print("Anchor Checking no reading because lost PLC connection")
				return -1
		else:
			return -1	#no connection

	def setDualBinFlap(self,side,val):
		if self.connected:
			if val:
				self.client.write_coil(DUAL_BIN_FLAP_ON+side, True)
			else:
				self.client.write_coil(DUAL_BIN_FLAP_OFF+side, True)

	def setFlipDuration_100ms(self,val):
		if self.connected:
			self.client.write_register(FLIP_DURATION_ADDR,val)

	def activateFurs(self,side):
		if self.connected:
			self.client.write_coil(FURS_ADDR+side, True)


	def close(self):
		self.client.close()
		print("Modbus TCP connection closed")