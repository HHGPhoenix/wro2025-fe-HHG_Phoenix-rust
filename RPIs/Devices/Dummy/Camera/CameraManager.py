import cv2
import numpy as np
import threading
import time
import uuid

# A class for detecting red and green blocks in the camera stream
class Camera():
    def __init__(self):
        """
        Initialize the camera and set up the color ranges for red and green blocks.
        """
        # Variable initialization
        self.freeze = False
        self.frame = None
        
        self.red_counter = []
        self.green_counter = []

        # Define the color ranges for green and red in HSV color space
        self.lower_green = np.array([53, 100, 40])
        self.upper_green = np.array([93, 220, 150])

        self.lower_red1 = np.array([0, 160, 120])
        self.upper_red1 = np.array([5, 220, 200])

        self.lower_red2 = np.array([173, 160, 100])
        self.upper_red2 = np.array([180, 220, 200])
        
        self.lower_black = np.array([0, 0, 0])
        self.upper_black = np.array([10, 10, 10])

        # Define the kernel for morphological operations
        self.kernel = np.ones((7, 7), np.uint8)

    def generate_random_image(self, width=1280, height=720):
        """
        Generate a random image for simulation purposes.

        Args:
            width (int, optional): The width of the generated image. Defaults to 1280.
            height (int, optional): The height of the generated image. Defaults to 720.

        Returns:
            np.ndarray: The generated random image in RGB color space.
        """
        # Generate a random image with random colors
        random_image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        return random_image

    def capture_array(self):
        """
        Capture an image from the camera and convert it to RGB and HSV color spaces.

        Returns:
            np.ndarray: The captured image in RGB color space.
            np.ndarray: The captured image in HSV color space.
        """
        frame = self.generate_random_image()
        frameraw = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framehsv = cv2.cvtColor(frameraw, cv2.COLOR_BGR2HSV)
        
        return frameraw, framehsv

    def simplify_image(self, framehsv, shade_of_red, shade_of_green):
        """
        Simplify the image by coloring red and green areas with specified shades.

        Args:
            framehsv (np.ndarray): The image in HSV color space.
            shade_of_red (list): The RGB values of the shade of red to color the red areas.
            shade_of_green (list): The RGB values of the shade of green to color the green areas.

        Returns:
            np.ndarray: The simplified image with red and green areas colored with the specified shades.
        """
        # Masks for green and red pixels
        mask_green = cv2.inRange(framehsv, self.lower_green, self.upper_green)
        mask_red1 = cv2.inRange(framehsv, self.lower_red1, self.upper_red1)
        mask_red2 = cv2.inRange(framehsv, self.lower_red2, self.upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        mask_black = cv2.inRange(framehsv, self.lower_black, self.upper_black)

        # Initialize a blank white image
        height, width = framehsv.shape[:2]
        simplified_image = np.ones((height, width, 3), np.uint8) * 255  # White background

        # Apply specified shades to red and green areas
        simplified_image[mask_green > 0] = shade_of_green
        simplified_image[mask_red > 0] = shade_of_red

        # Apply black color to non-red and non-green areas
        simplified_image[mask_black > 0] = [0, 0, 0]  # Black

        return simplified_image

    def draw_blocks(self, frameraw, framehsv):
        """
        Draw rectangles around green and red blocks in the camera stream.

        Args:
            frameraw (np.ndarray): The image in RGB color space.
            framehsv (np.ndarray): The image in HSV color space.

        Returns:
            np.ndarray: The image with rectangles drawn around green and red blocks.
        """
        # Create a mask of pixels within the green color range
        mask_green = cv2.inRange(framehsv, self.lower_green, self.upper_green)

        # Create a mask of pixels within the red color range
        mask_red1 = cv2.inRange(framehsv, self.lower_red1, self.upper_red1)
        mask_red2 = cv2.inRange(framehsv, self.lower_red2, self.upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # Dilate the masks to merge nearby areas
        mask_green = cv2.dilate(mask_green, self.kernel, iterations=1)
        mask_red = cv2.dilate(mask_red, self.kernel, iterations=1)

        # Find contours in the green mask
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find contours in the red mask
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cv2.circle(frameraw, (640, 720), 10, (255, 0, 0), -1)

        green_counter_set = False
        red_counter_set = False

        # Process each green contour
        for contour in contours_green:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 5 and h > 10:  # Only consider boxes larger than 50x50
                cv2.rectangle(frameraw, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frameraw, 'Green Object', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                cv2.line(frameraw, (640, 720), (int(x+w/2), int(y+h/2)), (0, 255, 0), 2)
                
                if green_counter_set == False:
                    self.green_counter.append(-1)
                    green_counter_set = True
        else:
            last_green_counter = self.green_counter[-1] if self.green_counter else 0
            if last_green_counter > 0 and last_green_counter < 30:
                self.green_counter.append(last_green_counter + 1)
                green_counter_set = True
                
            elif last_green_counter == -1:
                self.green_counter.append(1)    
                green_counter_set = True
                
            else:
                self.green_counter.append(0)
                green_counter_set = True
                
        if len(self.green_counter) > 10:
            self.green_counter.pop(0)

        # Process each red contour
        for contour in contours_red:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 5 and h > 10:  # Only consider boxes larger than 50x50
                cv2.rectangle(frameraw, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frameraw, 'Red Object', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                cv2.line(frameraw, (640, 720), (int(x+w/2), int(y+h/2)), (0, 0, 255), 2)
                
                if red_counter_set == False:
                    self.red_counter.append(-1)
                    red_counter_set = True
        else:
            last_red_counter = self.red_counter[-1] if self.red_counter else 0
            if last_red_counter > 0 and last_red_counter < 30:
                self.red_counter.append(last_red_counter + 1)
                red_counter_set = True
                
            elif last_red_counter == -1:
                self.red_counter.append(1)
                red_counter_set = True
                
            else:
                self.red_counter.append(0)
                red_counter_set = True
            
        return frameraw

    # Compress the video frames for the webstream    
    def compress_frame(self, frame, new_height=120):
        """
        Compress the frame to a specified height while maintaining the aspect ratio.

        Args:
            frame (np.ndarray): The frame to compress.
            new_height (int, optional): The height to compress the frame to. Defaults to 480.

        Raises:
            ValueError: If the number of dimensions in the frame is not 2 or 3.

        Returns:
            np.ndarray: The compressed frame.
        """
        dimensions = len(frame.shape)
        if dimensions == 3:
            height, width, _ = frame.shape
        elif dimensions == 2:
            height, width = frame.shape
        else:
            raise ValueError(f"Unexpected number of dimensions in frame: {dimensions}")
        new_width = int(new_height * width / height)
        frame = cv2.resize(frame, (new_width, new_height))
        frame = frame[10:, :]
        
        return frame

# Example usage
if __name__ == "__main__":
    camera = Camera()
    frameraw, framehsv = camera.capture_array()
    simplified_image = camera.simplify_image(framehsv, [255, 0, 0], [0, 255, 0])
    result_image = camera.draw_blocks(frameraw, framehsv)
    compressed_image = camera.compress_frame(result_image)

    # Display the images
    cv2.imshow('Raw Frame', frameraw)
    cv2.imshow('Simplified Image', simplified_image)
    cv2.imshow('Result Image', result_image)
    cv2.imshow('Compressed Image', compressed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
