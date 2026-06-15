#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        # Create a publisher for the /cmd_vel topic with a queue size of 10
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Set a timer to publish every 0.1 seconds (10Hz)
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Publishing linear velocity of 1.0 m/s to /cmd_vel')

    def timer_callback(self):
        msg = Twist()
        # Set linear velocity in the x-direction to 1.0 m/s
        msg.linear.x = 1.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        
        # Set angular velocity to 0.0 rad/s (moving straight)
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0
        
        self.publisher_.publish(msg)

def main(args=None):
    # Initialize the ROS 2 Python client library
    rclpy.init(args=args)
    
    velocity_publisher = VelocityPublisher()
    
    try:
        # Keep the node alive and processing callbacks
        rclpy.spin(velocity_publisher)
    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C
        pass
    finally:
        # Clean up the node
        velocity_publisher.destroy_node()
        # Safely shutdown rclpy only if it hasn't been shut down already
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()