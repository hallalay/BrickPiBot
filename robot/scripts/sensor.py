 #!/usr/bin/env python
import rospy
from std_msgs.msg import Bool
import brickpi3
 
class Sensor:
    def __init__(self):
       
        self.pub = rospy.Publisher('/touch/reading', Bool, queue_size = 10)
 
        self.BP = brickpi3.BrickPi3()
 
        self.BP.set_sensor_type(self.BP.PORT_1, self.BP.SENSOR_TYPE.TOUCH)
 
    def read(self):
        try:
            value = self.BP.get_sensor(self.BP.PORT_1)
            self.pub.publish(value)
        except brickpi3.SensorError:
            pass
 
    def reset(self):
        self.BP.reset_all()
 
 
 
 
if __name__ == '__main__':
 
    rospy.init_node('sensor', anonymous=True)
 
    s = Sensor()
    try:
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            s.read()
            rate.sleep()
           
    except rospy.ROSInterruptException():
        s.reset()
