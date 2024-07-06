import time
import threading
from RPIs.RPI_COM.messageReceiverServer import MessageReceiver
from RPIs.RPI_COM.sendMessage import Messenger
from RPIs.AIController.AICLib import AICU_Logger, RemoteFunctions, CommunicationEstablisher

from RPIs.Devices.Servo.servoClass import Servo

class AIController:
    def __init__(self):
        try:
            self.servo_pin = 4
            
            print("Starting AIController...")
            self.receiver = None
            self.client = None
            self.logger = None
            self.mode = None
            self.servo = None
            
            self.running = False
            
            self.x = 0.5
            self.y = 0.5
            self.rx = 0.5
            self.ry = 0.5
            
            self.communicationestablisher = CommunicationEstablisher(self)
            self.start_comm()

            self.logger.info("AIController started.")
            
            self.servo = self.initialize_components()
            
            self.logger.info("Spamming...")

            self.communicationestablisher.spam()
        
        except Exception as e:
            print(e)
            self.receiver.server_socket.close()

    def start_comm(self):
        self.remote_functions = RemoteFunctions(self)
        
        # Start the server
        self.receiver = MessageReceiver(r'RPIs/RPI_COM/Mappings/AIControllerMappings.json', 22222, handler_instance=self.remote_functions, ip='192.168.1.2')
        threading.Thread(target=self.receiver.start_server, daemon=True).start()

        self.client = Messenger('192.168.1.3', 11111)

        self.logger = AICU_Logger(self.client)
        
    def initialize_components(self):
        servo = Servo(self.servo_pin, minAngle=80, middleAngle=100, maxAngle=140)
        
        return servo

    def main_loop_opening_race(self):
        self.logger.info("Starting main loop for opening race...")
        
        while self.running:
            pass
        
    def main_loop_obstacle_race(self):
        self.logger.info("Starting main loop for obstacle race...")
        
        while self.running:
            pass
        
    def main_loop_training(self):
        self.logger.info("Starting main loop for training...")
        
        while self.running:
            servo_angle = self.servo.mapToServoAngle(self.x)
            self.servo.setAngle(servo_angle)
        
if __name__ == "__main__":
    try:
        ai_controller = AIController()
        while True:
            time.sleep(1)
    finally:
        ai_controller.running = False
        ai_controller.logger.log_info("Shutting down AIController...")
        ai_controller.receiver.server_socket.close()