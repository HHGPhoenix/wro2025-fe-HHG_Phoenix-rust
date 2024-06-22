from ....Misc.functionLibrary import find_usb_device
import serial

class LidarSensor():
    def __init__(self, usb_address=None):
        if usb_address is not None:
            self.ser_device = serial.Serial(usb_address, 115200)
        
        else:
            self.ser_device = find_usb_device(0x10c4, 0xea60)
            if self.ser_device is None:
                raise Exception("Lidar sensor not found, try specifying the USB address manually.")
            self.ser_device = serial.Serial(self.ser_device, 115200)
    
    def start_sensor(self):
        self.ser_device.open()
        self.ser_device.write(b'\xA5\x60')
        
    def stop_sensor(self):
        self.ser_device.write(b'\xA5\x25')
        self.ser_device.close()
        
    def read_data(self):
        return self.ser_device.read(9)