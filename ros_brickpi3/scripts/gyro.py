#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Imu
import brickpi3
import numpy as np

# Class for handle EV3 Gyro sensor inputs
class Gyro:
    def __init__(self, sensor_port = 1):

        # Init BrickPi3 instance and set up sensor port
        self.BP = brickpi3.BrickPi3()
        if sensor_port != 1:
            if sensor_port == 2:
                self.port = self.BP.PORT_2
            elif sensor_port == 3:
                self.port = self.BP.PORT_3
            elif sensor_port == 4:
                self.port = self.BP.PORT_4
            else:
                rospy.logwarn("[Gyro] Sensor input port '{}' not supported!".format(sensor_port))
        else:
            self.port = self.BP.PORT_1
        self.BP.set_sensor_type(self.port, self.BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)

        # ROS publisher
        self.pub = rospy.Publisher('/imu', Imu, queue_size = 10)
        self.last_val = None

    # Read and publish sesnor value
    def read(self):
        try:
            this_val = self.BP.get_sensor(self.port)
            if self.last_val is None:
                self.last_val = this_val
            else:
                if this_val[0] == 0 and abs(this_val[0] - self.last_val[0]) > 3:
                    this_val[0] = self.last_val[0]
            imu = Imu()
            imu.orientation.z = -this_val[0] * np.pi / 180.0
            while imu.orientation.z < -np.pi * 2.:
                imu.orientation.z += np.pi * 2.                    
            while imu.orientation.z > np.pi * 2.:
                imu.orientation.z -= np.pi * 2.
            if imu.orientation.z > np.pi:
                imu.orientation.z =  (imu.orientation.z - np.pi) - np.pi
            if imu.orientation.z < -np.pi:
                imu.orientation.z =  np.pi + (imu.orientation.z + np.pi)
            imu.orientation.w = 1.0
            imu.angular_velocity.z = -this_val[1] * np.pi / 180.0
            self.pub.publish(imu)
            self.last_val = this_val
        except brickpi3.SensorError as e:
            rospy.logwarn("[Gyro] Sensor error: {}".format(e))

    # Reset all sensor ports
    def reset(self):
        self.BP.reset_all()

        
# Conditional main 
if __name__ == '__main__':
        rospy.init_node('ev3_gyro_sensor', anonymous=True)
        g = Gyro()
        try:
            rate = rospy.Rate(10)
            while not rospy.is_shutdown():
                g.read()
                rate.sleep()
           
        except rospy.ROSInterruptException():
            g.reset()
