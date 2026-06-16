#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher_node')
        
        # 1. Declare parameters for easy configuration
        self.declare_parameter('video_device', '/dev/video0')
        self.declare_parameter('image_width', 1280)
        self.declare_parameter('image_height', 720)
        self.declare_parameter('fps', 30.0)
        
        # Get parameter values
        device = self.get_parameter('video_device').get_parameter_value().string_value
        width = self.get_parameter('image_width').get_parameter_value().integer_value
        height = self.get_parameter('image_height').get_parameter_value().integer_value
        fps = self.get_parameter('fps').get_parameter_value().double_value
        
        # 2. Create the Publisher
        self.publisher_ = self.create_publisher(Image, 'camera/image_raw', 10)
        
        # 3. Initialize CvBridge for converting OpenCV frames to ROS 2 messages
        self.bridge = CvBridge()
        
        # 4. Initialize OpenCV Video Capture
        self.get_logger().info(f"Opening camera device: {device}")
        self.cap = cv2.VideoCapture(device)
        
        if not self.cap.isOpened():
            self.get_logger().error(f"Failed to open camera device: {device}")
            raise RuntimeError(f"Could not open {device}")
            
        # Force MJPEG mode to unlock 720p @ 30 FPS on standard webcams
        self.cap.set(cv2.cv2.CAP_PROP_FOURCC if hasattr(cv2, 'cv2') else cv2.CAP_PROP_FOURCC, 
                     cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # 5. Create a timer to capture and publish frames at the desired FPS
        timer_period = 1.0 / fps
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info(f"Publishing camera stream at {width}x{height} @ {fps} FPS...")

    def timer_callback(self):
        ret, frame = self.cap.read()
        
        if ret:
            # Convert the raw OpenCV BGR image matrix to a ROS 2 Image message
            image_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            
            # Attach a timestamp header
            image_msg.header.stamp = self.get_clock().now().to_msg()
            image_msg.header.frame_id = 'camera_link_optical'
            
            # Publish the message
            self.publisher_.publish(image_msg)
        else:
            self.get_logger().warn("Failed to grab frame from camera stream.")

    def destroy_node(self):
        # Clean up hardware resources safely when closing down
        self.get_logger().info("Releasing camera resources.")
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    camera_publisher = CameraPublisher()
    
    try:
        rclpy.spin(camera_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        camera_publisher.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()