use evdev_rs::enums::{EventCode, EV_ABS};
use evdev_rs::Device;
use evdev_rs::ReadFlag;
use std::fs::File;
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone)]
pub struct PSController {
    pub x_val: i32,
    pub y_val: i32,
    pub rx_val: i32,
    pub ry_val: i32,
    pub device_path: &'static str,
}

pub fn new(device_path: &'static str) -> PSController {
    PSController {
        x_val: 128,
        y_val: 128,
        rx_val: 128,
        ry_val: 128,
        device_path: device_path,
    }
}

pub fn start_reading_thread(ps_controller: Arc<Mutex<PSController>>) {
    // Specify the device file of the DualShock 4 controller (example: /dev/input/event0)
    let file =
        File::open(ps_controller.lock().unwrap().device_path).expect("Could not open device file");
    let device = Device::new_from_file(file).expect("Failed to create new device");

    println!("Reading from DualShock 4 Controller...");

    let ps_controller_clone = Arc::clone(&ps_controller);
    let _ps_controller_thread = thread::spawn(move || {
        println!("Thread started.");
        loop {
            match device.next_event(ReadFlag::NORMAL) {
                Ok((_, ev)) => {
                    let mut ps_controller = ps_controller_clone.lock().unwrap();
                    match ev.event_code {
                        EventCode::EV_ABS(EV_ABS::ABS_X) => ps_controller.x_val = ev.value,
                        EventCode::EV_ABS(EV_ABS::ABS_Y) => ps_controller.y_val = ev.value,
                        EventCode::EV_ABS(EV_ABS::ABS_RX) => ps_controller.rx_val = ev.value,
                        EventCode::EV_ABS(EV_ABS::ABS_RY) => ps_controller.ry_val = ev.value,
                        _ => {} // Ignore other types of events
                    }
                }
                Err(e) => {
                    println!("Error reading event: {:?}", e);
                    break;
                }
            }
        }
        println!("Thread exiting.");
    });
}
