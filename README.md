raspberry-pi-pid-pwm-fan
===
A Python script to regulate Raspberry Pi CPU temperature using PID tuned PWM fan.

## Hardware

Fritzing breadboard connection:

![Fritzing](fritzing.png)

Notice the base of the PNP transistor is connected to GPIO 18 (or pin 12) which is the only PWM enabled pin on Raspberry Pi GPIO. The emitter of the transistor is connected to the GPIO ground, and the collector of the transistor is connected to the negative terminal of the fan. Optional back EMF diode and small capacitor are recommended, which were not shown in the sketch.

## Required Python Packages

Update Linux packages:
```
sudo apt-get update
```

Install Python 3 if not available:
```
sudo apt-get install python3.6
```

Install gpiozero package
```
sudo apt install python3-gpiozero
```

## Local Test

You can test if the Python script works by running:
```
python3 pwm_fan.py
```

## Copy Files

### Copy pwm_fan.py Python Script

```
sudo cp pwm_fan.py /usr/local/bin/pwm_fan.py
sudo chmod +x pwm_fan.py
```

### Copy pwm_fan Shell Script

```
sudo cp pwm_fan /etc/init.d/pwm_fan
sudo chmod +x pwm_fan
```

### Run update-rc

```
sudo update-rc.d pwm_fan defaults
```

### Verify

```
/etc/init.d/pwm_fan start
```

If you see error like ```-bash: /etc/init.d/pwm_fan: /bin/sh^M: bad interpreter:
No such file or directory```, it means the bash file format is incorrect.

To fix this:
```
vi /etc/init.d/pwm_fan
```
then type ```:set ff=unix```, then save with ```wq!```.

### Reboot

```
sudo reboot
```

## Tuning

Although the script comes with default parameters to provide an adequate tuning. You can supply any of the following arguments when constructing the `PidPwmFan` class to achieve optimal performance.

```
pin (int):           The PWM pin number on RPi (default is 18)
loop_int (float):    The loop interval of the PID loop (seconds)
pwm_freq (float):    The PWM frequency (Hz)
pwm_min (float):     The minimum PWM value (0 ~ 1.0)
pwm_max (float):     The maximum PWM value (0 ~ 1.0)
target_temp (float): The desired CPU temperature (degree Celsius)
pid (tuple):         Kp, Ki and Kd for PID tuning
init_pwm (float):    Initial PWM value (0 ~ 1.0)
window_int (float):  Window interval to keep past error measurements (seconds)
```
