use rppal::pwm::{Channel, Polarity, Pwm};

pub struct Servo {
    pub pwm: Pwm,
    pub rpi_pin: u8,
}

pub fn new(rpi_pin: u8) -> Servo {
    let pwm = Pwm::with_frequency(Channel::Pwm0, 50.0, 0.175, Polarity::Normal, true)
        .expect("Failed to initialize PWM");

    Servo {
        pwm: pwm,
        rpi_pin: rpi_pin,
    }
}

pub fn set_angle(servo: &Servo, angle: f64) {
    let duty_cycle = angle_to_duty_cycle(angle);
    servo
        .pwm
        .set_duty_cycle(duty_cycle)
        .expect("Failed to set duty cycle");
    println!("Setting servo angle to {} degrees.", angle);
}

fn angle_to_duty_cycle(angle: f64) -> f64 {
    // Convert angle to duty cycle (example conversion)
    let min_duty = 0.14; // 5%
    let max_duty = 0.22; // 10%
    min_duty + (angle as f64 / 180.0) * (max_duty - min_duty)
}
