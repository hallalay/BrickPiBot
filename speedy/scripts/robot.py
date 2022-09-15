import rospy
from geometry_msgs.msg import Pose2D
from std_msgs.msg import Int16
import brickpi3
import numpy as np

class Robot:
    def __init__(self):


        # Create ROS subscribers for positions
        rospy.Subscriber('/cheeky_nandos/rp2/position', Pose2D, self.robot_position_callback)
        rospy.Subscriber('/cheeky_nandos/ball/position', Pose2D, self.target_position_callback)
        self.robot_x, self.robot_y, self.robot_th = None, None, None
        self.target_x, self.target_y = 2.08, 0.0

        #rospy.Subscriber('/speedy/linear', Int16, self.linear_velocity_callback)
        #rospy.Subscriber('/speedy/angular', Int16, self.angular_velocity_callback)
        
        # Create BrickPi3 instance and motors
        self.BP = brickpi3.BrickPi3()
        self.motor_left_port =  self.BP.PORT_C
        self.motor_right_port = self.BP.PORT_B
        self.lin_vel = 50
        self.ang_vel = 20

    # Callback functions
    def robot_position_callback(self, msg):
        self.robot_x, self.robot_y, self.robot_th = msg.x, msg.y, msg.theta
        '''
        rospy.loginfo('x: {:.2f}'.format(msg.x))
        rospy.loginfo('y: {:.2f}'.format(msg.y))
        rospy.loginfo('th: {:.2f}'.format(msg.theta))
        rospy.loginfo('---------')
        '''
        
    def target_position_callback(self, msg):
        self.target_x, self.target_y = msg.x, msg.y
        if self.robot_x is not None and self.robot_y is not None:
            diff_x = self.target_x - self.robot_x
            diff_y = self.target_y - self.robot_y
            dist = np.sqrt( diff_y * diff_y + diff_x * diff_x )
            if dist < 0.2:
                self.target_x, self.target_y = 4.16, 0.0
                self.lin_vel = 100
            else:
                self.lin_vel = 50

    def linear_velocity_callback(self, msg):
        self.lin_vel = msg.data
        rospy.loginfo('Linear velocity: {}'.format(self.lin_vel))
    def angular_velocity_callback(self, msg):
        self.ang_vel = msg.data
        rospy.loginfo('Angular velocity: {}'.format(self.ang_vel))
        
    def change_velocity(self, key):
        if key == 'a':
            self.lin_vel -= 1
        if key == 's':
            self.lin_vel += 1
        if key == 'q':
            self.ang_vel -= 1
        if key == 'w':
            self.ang_vel += 1
        rospy.loginfo('Distance: {:.2f} (m)'.format(dist))
        rospy.loginfo('Rotation: {:.2f} (rad)'.format(rot))

            
        
    # ROS main loop
    def drive(self):
        if self.robot_x is not None and self.robot_y is not None and self.target_x is not None and self.target_y is not None:  
            diff_x = self.target_x - self.robot_x
            diff_y = self.target_y - self.robot_y
            dist = np.sqrt( diff_y * diff_y + diff_x * diff_x )
            rot = np.arctan2(diff_y, diff_x) - self.robot_th - np.pi / 2
            if rot > np.pi:
                rot = rot - 2 * np.pi
            elif rot < -np.pi:
                rot = rot + 2 * np.pi
            rospy.loginfo('Distance: {:.2f} (m)'.format(dist))
            rospy.loginfo('Rotation: {:.2f} (rad)'.format(rot))
            lin = (1.0 - (dist / 4.9)) * self.lin_vel
            ang = (rot / np.pi) * self.ang_vel
            left_speed = int(lin - ang)
            right_speed = int(lin + ang)
            rospy.loginfo('Left speed: {:.2f}'.format(left_speed))
            rospy.loginfo('Right speed: {:.2f}'.format(right_speed))
            rospy.loginfo('---------')
            #self.robot_x, self.robot_y, self.robot_th = None, None, None
            if left_speed > 100:
                left_speed = 100
            elif left_speed < -100:
                left_speed = -100
            if right_speed > 100:
                right_speed = 100
            elif right_speed < -100:
                right_speed = -100
            self.BP.set_motor_power(self.motor_left_port, left_speed)
            self.BP.set_motor_power(self.motor_right_port, right_speed)
            
            
    # Method for "unconfigure" all sensors and motors
    def reset(self):
        self.BP.reset_all()

        
# Main function
if __name__ == '__main__':

        # Init the connection with the ROS system
        rospy.init_node('speedy_robot', anonymous=True)

        # Create and run the robot
        robot = Robot()
        try:
            rate = rospy.Rate(10)
            while not rospy.is_shutdown():
                robot.drive()
                rate.sleep()    
        except rospy.ROSInterruptException:
            robot.reset()
