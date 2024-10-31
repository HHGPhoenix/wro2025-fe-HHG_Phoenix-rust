use serialport::SerialPort;
use std::io::Write;
use std::time::Duration;

pub struct MotorController {
    port: Box<dyn SerialPort>,
}

pub fn new(device_path: &str, baudrate: u32) -> MotorController {
    let mut port = serialport::new(device_path, baudrate)
        .timeout(Duration::from_millis(100))
        .open()
        .expect("Failed to open serial port");

    match port.write(b"SPEED 50\n") {
        Ok(_) => println!("Speed command sent successfully"),
        Err(e) => eprintln!("Failed to write to serial port: {}", e),
    }

    MotorController { port }
}

pub fn set_speed(motor_controller: &mut MotorController, speed: i32) {
    let mut speed = speed;
    if speed < -255 {
        speed = -255;
    } else if speed > 255 {
        speed = 255;
    } else if speed > -10 && speed < 10 {
        speed = 0;
    }

    let speed_str = format!("SPEED {}\n", speed);
    println!("Formatted speed command: {}", speed_str);

    match motor_controller.port.write(speed_str.as_bytes()) {
        Ok(_) => println!("Speed command sent successfully: {}", speed_str),
        Err(e) => eprintln!("Failed to write to serial port: {}", e),
    }
}
