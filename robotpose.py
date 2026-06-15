import rclpy
from rclpy.node import Node

# Message and library imports
from turtlesim.msg import Pose as TurtlePose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import TransformStamped # NEW: Import for Transform messages
from tf2_ros import TransformBroadcaster      # NEW: The library for broadcasting transforms
from tf_transformations import quaternion_from_euler

class PoseAndTfTranslator(Node):
    def __init__(self):
        super().__init__('pose_and_tf_translator')
        

        self.pose_subscriber = self.create_subscription(
            TurtlePose,
            '/turtle1/pose',
            self.turtle_pose_callback,
            10)
            
        self.pose_stamped_publisher = self.create_publisher(
            PoseStamped,
            '/turtle1/pose_stamped',
            10)
            


    def turtle_pose_callback(self, msg: TurtlePose):
        # --- Part 1: Publish the PoseStamped message ---
        pose_stamped_msg = PoseStamped()
        current_time = self.get_clock().now().to_msg()

        pose_stamped_msg.header.stamp = current_time
        pose_stamped_msg.header.frame_id = 'world'

        pose_stamped_msg.pose.position.x = msg.x
        pose_stamped_msg.pose.position.y = msg.y
        pose_stamped_msg.pose.position.z = 0.0

        q = quaternion_from_euler(0, 0, msg.theta)
        pose_stamped_msg.pose.orientation.x = q[0]
        pose_stamped_msg.pose.orientation.y = q[1]
        pose_stamped_msg.pose.orientation.z = q[2]
        pose_stamped_msg.pose.orientation.w = q[3]

        self.pose_stamped_publisher.publish(pose_stamped_msg)




def main(args=None):
    rclpy.init(args=args)
    node = PoseAndTfTranslator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
