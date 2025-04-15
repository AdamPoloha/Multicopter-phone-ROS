#!/usr/bin/env python
'''
Developer: Adam Poloha
Date: 20 November 2024
Node: Drone Phone Sensors Node Publisher
'''

#Run "rosrun rviz rviz -f FNC_phone_frame" to start rviz

#Should have 51uT Near New Zealand of geomagnetic field

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import numpy as np
import socket
import json

class Drone_phone_Pub(Node):
	def __init__(self):
		super().__init__('Drone_phone_Pub_object')
		self.get_logger().info("IMU Node Initialization")
		
		self._Drone_FNC_phone_data_pub = self.create_publisher(Imu, 'Drone_FNC_phone_data', 10)
		self.timer = self.create_timer(0.001, self.read_and_pub)  # 1000 Hz
		self._Drone_FNC_phone_data_msg = Imu()

		self.get_logger().info("Phone Sensors Node")

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #python2 compatible

		HOST = "127.0.0.1" #sys.argv[1]
		PORT = 1234

		#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		while True:
			try:
				self.s.bind((HOST, PORT))
				break
			except:
				try:
					#s.shutdown(socket.SHUT_RDWR)
					self.s.close()
					self.get_logger().info("Closed")
				except:
					self.get_logger().info("Could not close")
					exit()

		self.s.listen(0)
		self.conn, addr = self.s.accept()
		self.get_logger().info("Connected by" + str(addr))
		
		self.cgdiff = np.matrix([0.0, 0.0, 0.0, 0.0])
		self.Firstmag = 0
		self.acceptrange = 1.1 #1.1 -1.0 = 0.2 = 10%
	
	def orientswitch(self, gamequatr, geoquatr, mag):
		#print(mag)
		#print(np.linalg.norm(mag))
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
		switched = np.divide((np.multiply(gyroscope, gyroK) + np.multiply(compass, compK)), gyroK + compK)
		#print("Fused")
		return switched
	
	"""
	"Game Rotation Vector Sensor","GeoMag Rotation Vector Sensor","bmi160 GYROSCOPE","bmi160 ACCELEROMETER","akm09915 MAGNETOMETER"
	Mag, Acc, Geo, Gyro, Game
	"""
	
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
					content = jsdict[u'akm09915 MAGNETOMETER']
					magvect = content[u'values']
					mag = True
				except:
					a = 0
				try:
					content = jsdict[u'bmi160 ACCELEROMETER']
					accels = content[u'values']
					accel = True
				except:
					a = 0
				try:
					content = jsdict[u'GeoMag Rotation Vector Sensor']
					geoquatr = content[u'values']
					geo = True
				except:
					a = 0
				try:
					content = jsdict[u'bmi160 GYROSCOPE']
					gyroeul = content[u'values']
					gyro = True
				except:
					a = 0
				try:
					content = jsdict[u'Game Rotation Vector Sensor']
					gamequatr = content[u'values']
					game = True
				except:
					a = 0
			except:
				#print("Not JSON format")
				a = 0
		
		orient = self.orientswitch(gamequatr, geoquatr, magvect)
		#print(orient.shape)

		self._Drone_FNC_phone_data_msg.header.stamp = self.get_clock().now().to_msg()
		self._Drone_FNC_phone_data_msg.header.frame_id = "FNC_phone_frame"
		self._Drone_FNC_phone_data_msg.linear_acceleration.x = float(accels[0])  # linear acceleration x (m/s^2)
		self._Drone_FNC_phone_data_msg.linear_acceleration.y = float(accels[1])  # linear acceleration y (m/s^2)
		self._Drone_FNC_phone_data_msg.linear_acceleration.z = float(accels[2])  # linear acceleration z (m/s^2)
		self._Drone_FNC_phone_data_msg.angular_velocity.x = float(gyroeul[0]) # angular velocity x (rad/s)
		self._Drone_FNC_phone_data_msg.angular_velocity.y = float(gyroeul[1]) # angular velocity y (rad/s)
		self._Drone_FNC_phone_data_msg.angular_velocity.z = float(gyroeul[2]) # angular velocity z (rad/s)
		self._Drone_FNC_phone_data_msg.orientation.x = float(orient.item(0))
		self._Drone_FNC_phone_data_msg.orientation.y = float(orient.item(1))
		self._Drone_FNC_phone_data_msg.orientation.z = float(orient.item(2))
		self._Drone_FNC_phone_data_msg.orientation.w = float(orient.item(3))

		#print("Publishing")
		self._Drone_FNC_phone_data_pub.publish(self._Drone_FNC_phone_data_msg)

		#self.closeport()

	def closeport(self):
		self.get_logger().info("Closing phone sensors socket")
		try:
			#s.shutdown(socket.SHUT_RDWR)
			self.s.close()
			self.get_logger().info("Closed")
		except:
			self.get_logger().info("Could not close")

def main(args=None):
	rclpy.init(args=args)
	Drone_phone_Pub_object = Drone_phone_Pub()
	try:
		rclpy.spin(Drone_phone_Pub_object)
	except Exception as e:
		print(e)
		Drone_phone_Pub_object.closeport()
	Drone_phone_Pub_object.destroy_node()
	print("Shutting down")
	rclpy.shutdown()

if __name__ == '__main__':
	main()
