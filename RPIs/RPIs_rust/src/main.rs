use devices::motor_controller;
use devices::ps_controller;
use devices::servo;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

// Declare the module path
mod devices {
    pub mod motor_controller;
    pub mod ps_controller;
    pub mod servo;
}

// Use the ps_controller module

const DEVICE_PATH: &str = "/dev/input/event4";

fn main() {
    let controller = ps_controller::new(DEVICE_PATH);
    let controller_arc = Arc::new(Mutex::new(controller));
    ps_controller::start_reading_thread(controller_arc.clone());

    let servo = servo::new(4);

    let mut motor_controller = motor_controller::new("/dev/ttyUSB0", 921600);

    loop {
        {
            let controller = controller_arc.lock().unwrap();
            println!(
                "x: {}, y: {}, rx: {}, ry: {}",
                controller.x_val, controller.y_val, controller.rx_val, controller.ry_val
            );
            servo::set_angle(&servo, controller.x_val as f64 * 0.7);
            motor_controller::set_speed(&mut motor_controller, (controller.ry_val - 128) * -2);
        }
        thread::sleep(Duration::from_millis(20));
    }
}
