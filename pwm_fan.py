#!/usr/bin/python3

import sys
import gpiozero
import time
import collections

class PidPwmFan:
    """
    PWM fan CPU temperature sensing PID controller for RPi.
    """

    def __init__(
        self,
        pin=18,
        loop_int=0.1,
        pwm_freq=60,
        pwm_min=0.1,
        pwm_max=0.9,
        target_temp=35,
        pid=(0.03, 0.005, 0.02),
        init_pwm=0.5,
        window_int=10):
        """PwmFan class constructor.

        Args:
            pin (int):           The PWM pin number on RPi (default is 18)
            loop_int (float):    The loop interval of the PID loop (seconds)
            pwm_freq (float):    The PWM frequency (Hz)
            pwm_min (float):     The minimum PWM value (0 ~ 1.0)
            pwm_max (float):     The maximum PWM value (0 ~ 1.0)
            target_temp (float): The desired CPU temperature (degree Celsius)
            pid (tuple):         Kp, Ki and Kd for PID tuning
            init_pwm (float):    Initial PWM value (0 ~ 1.0)
            window_int (float):  Window interval to keep past error measurements (seconds)
        """
        self.pin = pin
        self.loop_int = loop_int
        self.pwm_freq = pwm_freq
        self.pwm_min = pwm_min
        self.pwm_max = pwm_max
        self.target_temp = target_temp
        if len(pid) != 3:
            raise Exception('Invalid PID gains.')
        self.pid = pid
        if init_pwm < 0.0 or init_pwm > 1.0:
            raise Exception("Invalid initial PWM value.")
        self.init_pwm = init_pwm
        self.window_int = window_int

        self.pwm = gpiozero.PWMLED(pin=pin, frequency=pwm_freq)
        self.cpu = gpiozero.CPUTemperature()
        self.cpu_temp = self.cpu.temperature
        # The next PWM value to be updated.
        self.value = init_pwm
        # The queue of past error measurements.
        self.window_size = int(window_int / loop_int)
        self.errors = collections.deque(self.window_size * [(0, time.time())], self.window_size)

    def __Measure(self):
        """
        Takes a measurement of the temperature difference and add the current
        temperature difference and measurement timestamp to the queue.
        """
        self.cpu_temp = self.cpu.temperature
        error = self.cpu_temp - self.target_temp
        self.errors.appendleft((error, time.time()))

    def __CalculatePwmDelta(self):
        """
        Calculates the PID updates based on current error measurements.

        Returns:
            float: The calculated PID update value.
        """
        self.dP = self.pid[0] * self.errors[0][0]
        self.dI = 0
        for i in range(len(self.errors)):
            self.dI += self.errors[i][0]
        self.dI = self.dI * self.pid[1] / self.window_size / self.loop_int
        self.dD = self.pid[2] * (self.errors[0][0] - self.errors[1][0]) / self.loop_int
        return self.dP + self.dI + self.dD

    def __UpdatePwmValue(self, delta):
        self.value += delta
        if self.value < self.pwm_min:
            self.value = self.pwm_min
        elif self.value > self.pwm_max:
            self.value = self.pwm_max
        else:
            self.value = self.value

    def Update(self):
        """
        Updates the PWM value based on a new measurement and PID gains.
        """
        self.__Measure()
        delta = self.__CalculatePwmDelta()
        self.__UpdatePwmValue(delta)
        self.pwm.value = self.value

    def Start(self):
        """
        Starts PID loop.
        """
        while True:
            self.Update()
            # For logging.
            print('current_temp=%3.3f, target_temp=%3.3f' %
                (self.cpu.temperature, self.target_temp))
            print('dP=%2.3f, dI=%2.3f, dD=%2.3f, d=%2.3f' %
                (self.dP, self.dI, self.dD, self.dP + self.dI + self.dD))
            print('pwm_value=%1.3f' % self.value)
            for i in range(0, 3):
                sys.stdout.write("\033[F")
            # Sleep loop_int second.
            time.sleep(self.loop_int)

# Main to use the PidPwmFan class.
fan = PidPwmFan()
fan.Start()
