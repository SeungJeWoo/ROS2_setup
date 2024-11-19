#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

# import the message type to use
from std_msgs.msg import Int64, Bool
from geometry_msgs.msg import Twist  # Import Twist for velocity commands

class ConstantControl(Node):
    def __init__(self) -> None:
		# initialize base class (must happen before everything else)
        super().__init__("constant_control")	
        self.get_logger().info("Constant Control Node has been started.")
    
        # Create a publisher for the /cmd_vel topic
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
    
        # Create a timer that triggers every 0.2 seconds
        self.timer = self.create_timer(0.2, self.timer_callback)

        # Subscriber for /kill topic
        self.kill_subscriber = self.create_subscription(
            Bool,
            '/kill',
            self.kill_callback,
            10
        )
        self.get_logger().info("Subscribed to /kill topic")
        
        # Subscriber for /resume topic
        self.resume_subscriber = self.create_subscription(
            Bool,
            '/resume',
            self.resume_callback,
            10
        )
        self.get_logger().info("Subscribed to /resume topic")


    def timer_callback(self):
        # Construct a Twist message
        msg = Twist()
        msg.linear.x = 0.5  # Forward linear velocity
        msg.angular.z = 0.1  # Rotational velocity

        # Publish the message
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: linear.x={msg.linear.x}, angular.z={msg.angular.z}")

    def kill_callback(self, msg):
        """
        Callback for /kill topic. Stops the robot when True is received.
        """
        if msg.data:  # If the kill signal is True
            self.get_logger().info("Kill signal received! Stopping the robot.")
            
            # Cancel the timer
            self.timer.cancel()
            
            # Publish a zero velocity message
            stop_msg = Twist()
            self.publisher_.publish(stop_msg)
            self.get_logger().info("Published zero velocity to /cmd_vel.")
    
    def resume_callback(self, msg):
        """
        Callback for /resume topic. Restarts the timer if True is received.
        """
        if msg.data:  # If the resume signal is True
            self.get_logger().info("Resume signal received! Restarting the robot.")
            
            # Restart the timer if it's not already running
            if not self.timer.is_canceled():
                self.get_logger().info("Timer is already running. Ignoring resume signal.")
                return
            
            # Restart the timer
            self.timer = self.create_timer(0.2, self.timer_callback)
            self.get_logger().info("Timer restarted. Publishing constant velocity.")



if __name__ == "__main__":
    rclpy.init()        # initialize ROS2 context (must run before any other rclpy call)
    node = ConstantControl()  # instantiate the heartbeat node
    rclpy.spin(node)    # Use ROS2 built-in schedular for executing the node
    rclpy.shutdown()    # cleanly shutdown ROS2 context