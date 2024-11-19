#!/usr/bin/env python
'''
Developer: Adam Poloha
Date: 20 November 2024
Node: Drone Phone Sensors Node Publisher
'''

#Run "rosrun rviz rviz -f FNC_phone_frame" to start rviz

#Should have 51uT Near New Zealand of geomagnetic field

from sensor_msgs.msg import Imu
import rospy
import numpy as np
import socket
import json

class Drone_phone_Pub(object):
	def __init__(self):
		rospy.loginfo("IMU Node Initialization")

		self._Drone_FNC_phone_data_pub = rospy.Publisher('Drone_FNC_phone_data', Imu, queue_size=1)
		self._Drone_FNC_phone_data_msg = Imu()
		rospy.loginfo("Phone Sensors Node")

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #python2 compatible

		HOST = "127.0.0.1" #"192.168.42.129" #sys.argv[1]
		PORT = 1234

		#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		try:
			self.s.bind((HOST, PORT))
		except:
			try:
				#s.shutdown(socket.SHUT_RDWR)
				self.s.close()
				print("Closed")
			except:
				print("Could not close")
				exit()

		self.s.listen(0)
		self.conn, addr = self.s.accept()
		print("Connected by", addr)
		
		self.cgdiff = np.matrix([0.0, 0.0, 0.0, 0.0])
		self.Firstmag = 0
		self.acceptrange = 1.1 #1.1 -1.0 = 0.2 = 10%

	def orientswitch(self, gamequatr, geoquatr, mag):
		print(mag)
		print(np.linalg.norm(mag))
		if (self.Firstmag == 0):
			self.Firstmag = np.linalg.norm(mag)
		gyroscope = np.matrix(gamequatr)
		compass = np.matrix([geoquatr[0], geoquatr[1], geoquatr[2], geoquatr[3]]) #5 values, last is always zero
		
		if(np.linalg.norm(mag) >= (self.Firstmag * self.acceptrange)): #Compass bad
			gyroK = np.matrix([1.0, 1.0, 1.0, 1.0])
			compK = np.matrix([0.0, 0.0, 0.0, 0.0])
			gyroscope = gyroscope - self.cgdiff
			print("Gyroscope")
		else:
			gyroK = np.matrix([0.0, 0.0, 0.0, 0.0])
			compK = np.matrix([1.0, 1.0, 1.0, 1.0])
			self.cgdiff = gyroscope - compass #Always renew offset+drift
			print("Compass")
		#fused = np.matrix([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
		
		#print(np.linalg.norm(compass))
		
		#print(gyroscope, gyroK, compass, compK)
		#print("Fusing")
		fused = np.divide((np.multiply(gyroscope, gyroK) + np.multiply(compass, compK)), gyroK + compK)
		#print("Fused")
		return fused

	def read_and_pub(self):
		
		geo = False
		game = False
		accel = False
		mag = False
		gyro = False
		
		while True: #c < 120000: #At -d 5, this loop runs at 200Hz
			#print(gyro, geo)
			if geo == True and game == True and accel == True and mag == True and gyro == True:
				#print("Got all data")
				break
			data = self.conn.recv(1024) # Grab data from socket
			#print(data)
			if not data:
				break
			#print(c)
			#print(data)
			try:
				jsdict = json.loads(data) # Convert to json
				#print(jsdict)
				try:
					content = jsdict[u'geomagnetic Rotation Vector']
					geoquatr = content[u'values']
					geo = True
				except:
					a = 0
				try:
					content = jsdict[u'game Rotation Vector']
					gamequatr = content[u'values']
					game = True
				except:
					a = 0
				try:
					content = jsdict[u'accelerometer']
					accels = content[u'values']
					accel = True
				except:
					a = 0
				try:
					content = jsdict[u'mag-akm09911']
					magvect = content[u'values']
					mag = True
				except:
					a = 0
				try:
					content = jsdict[u'gyroscope-lsm6ds3']
					gyroeul = content[u'values']
					gyro = True
				except:
					a = 0
			except:
				#print("Not JSON format")
				a = 0
		
		orient = self.orientswitch(gamequatr, geoquatr, magvect)
		#print(orient.shape)

		self._Drone_FNC_phone_data_msg.header.stamp = rospy.Time.now()
		self._Drone_FNC_phone_data_msg.header.frame_id = "FNC_phone_frame"
		self._Drone_FNC_phone_data_msg.linear_acceleration.x = accels[0]  # linear acceleration x (m/s^2)
		self._Drone_FNC_phone_data_msg.linear_acceleration.y = accels[1]  # linear acceleration y (m/s^2)
		self._Drone_FNC_phone_data_msg.linear_acceleration.z = accels[2]  # linear acceleration z (m/s^2)
		self._Drone_FNC_phone_data_msg.angular_velocity.x = gyroeul[0] # angular velocity x (rad/s)
		self._Drone_FNC_phone_data_msg.angular_velocity.y = gyroeul[1] # angular velocity y (rad/s)
		self._Drone_FNC_phone_data_msg.angular_velocity.z = gyroeul[2] # angular velocity z (rad/s)
		self._Drone_FNC_phone_data_msg.orientation.x = orient.item(0)
		self._Drone_FNC_phone_data_msg.orientation.y = orient.item(1)
		self._Drone_FNC_phone_data_msg.orientation.z = orient.item(2)
		self._Drone_FNC_phone_data_msg.orientation.w = orient.item(3)

		#print("Publishing")
		self._Drone_FNC_phone_data_pub.publish(self._Drone_FNC_phone_data_msg)

		#self.closeport()

	def closeport(self):
		try:
			#s.shutdown(socket.SHUT_RDWR)
			self.s.close()
			print("Closed")
		except:
			print("Could not close")

	def shutdownhook(self):
		rospy.loginfo("Shut Down.")
		rospy.loginfo("Closing phone sensors socket")
		self.closeport()
		rospy.loginfo("Done")
		ctrl_c = True
		#exit()

if __name__ == '__main__':
	rospy.init_node('Drone_phone_Pub_node')
	Drone_phone_Pub_object = Drone_phone_Pub()
	rate = rospy.Rate(100) # loop Hz
	ctrl_c = False

	rospy.on_shutdown(Drone_phone_Pub_object.shutdownhook)
	while not ctrl_c:
		try:
			Drone_phone_Pub_object.read_and_pub()
			rate.sleep()
		except KeyboardInterrupt:
			rospy.loginfo("Closing IMU Port")
			Drone_phone_Pub_object.closeport()
			rospy.loginfo("Done")
			ctrl_c = True
			#exit()
		except IOError:
			rospy.loginfo("Port is closed")
			exit()
		except Exception as e:
			rospy.loginfo(e)
			exit()