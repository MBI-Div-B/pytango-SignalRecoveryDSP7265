#!/usr/bin/env python3
#

import sys
import os
import time
from enum import IntEnum
import numpy as np

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt
from tango.server import Device, attribute, command, pipe, device_property

from pymeasure.instruments.signalrecovery import DSP7265 as DSP

class DSP7265(Device):

    # -----------------
    # Device Properties
    # -----------------

    address = device_property(dtype='DevString', default_value = 'GPIB::12::INSTR')
    ref = device_property(dtype='DevString', default_value = 'internal')

    # ----------
    # Attributes
    # ----------

    x = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ,
        label="X",
        unit="nV",
        format="%6.2f",
        doc="signal X component",
    )

    y = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ,
        label="Y",
        unit="nV",
        format="%6.2f",
        doc="signal Y component"
    )

    R = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ,
        label="R",
        unit="nV",
        format="%6.2f",
        doc="signal R component"
    )

    Theta = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ,
        label="Theta",
        unit="deg",
        format="%6.2f",
        doc="signal Theta component"
    )
        
    timeconstant = attribute(dtype = 'DevEnum',
        label = 'time constant',
        enum_labels = ['10 us','20 us', '40 us', '80 us', '160 us', '320 us', '640 us', '5 ms', '10 ms', '20 ms',
            '50 ms', '100 ms', '200 ms', '500 ms', '1 s', '2 s', '5 s', '10 s', '20 s', '50 s', '100 s', '200 s',
            '500 s', '1 ks', '2 ks', '5 ks', '10 ks', '20 ks', '50 ks'],
        access = AttrWriteType.READ_WRITE,)

    sensitivity = attribute(dtype = 'DevEnum',
        label = 'sensitivity',
        enum_labels = ['nan', '2 nV', '5 nV', '10 nV', '20 nV', '50 nV', '100 nV', '200 nV', '500 nV',
            '1 uV', '2 uV', '5 uV', '10 uV', '20 uV', '50 uV', '100 uV', '200 uV', '500 uV',
            '1 m', '2 mV', '5 mV', '10 mV', '20 mV', '50 mV', '100 mV', '200 mV', '500 mV', '1 V'],
        access = AttrWriteType.READ_WRITE,)
    
    gain = attribute(dtype = 'DevEnum',
        label = 'AC gain',
        enum_labels = ['0 db', '10 db', '20 db', '30 db', '40 db', '50 db', '60 db', '70 db', '80 db', '90 db'],
        access = AttrWriteType.READ_WRITE,)
    
    slope = attribute(dtype = 'DevEnum',
        label = 'filter slope',
        enum_labels = ['6 db/octave', '12 db/octave', '18 db/octave', '24 db/octave'],
        access = AttrWriteType.READ_WRITE,)
    
    frequency = attribute(dtype = 'DevFloat',
        label = 'reference frequency',
        access = AttrWriteType.READ_WRITE,
        unit = 'Hz',
        min_value = 0.001,
        max_value = 250000,
        format="%8.3f",)  
    
    reference = attribute(dtype = 'DevEnum',
        label = 'reference',
        enum_labels = ['internal', 'external rear', 'external front'],
        access = AttrWriteType.READ_WRITE,)  
    
    ACcoupling = attribute(dtype = 'DevBoolean',
        label = 'AC coupling',
        access = AttrWriteType.READ_WRITE,)

    ground = attribute(dtype = 'DevBoolean',
        label = 'Ground shielding',
        access = AttrWriteType.READ_WRITE,)
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.device = DSP(self.address)
        self.SLOPES = [6, 12, 18, 24]
        self.GAINS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        self.set_state(DevState.ON)

    # ------------------
    # Attributes methods
    # ------------------
    
    ### READ COMMANDS ###

    def read_x(self):
        return 10**9*self.device.x
    
    def read_y(self):
        return 10**9*self.device.y
    
    def read_R(self):
        return 10**9*self.device.mag
    
    def read_Theta(self):
        return self.device.phase

    def read_timeconstant(self):
        tc = np.ones(29)*self.device.time_constant
        return int(np.sum(np.arange(29)*(tc == self.device.TIME_CONSTANTS)))

    def read_sensitivity(self):
        sens = np.ones(28)*self.device.sensitivity
        return int(np.sum(np.arange(28)*(sens == self.device.SENSITIVITIES)))

    def read_gain(self):
        g = 10*np.ones(10)*self.device.gain[0]
        return int(np.sum(np.arange(10)*(g == self.GAINS)))
    
    def read_slope(self):
        sl = np.ones(4)*self.device.slope
        return int(np.sum(np.arange(4)*(sl == self.SLOPES)))

    def read_frequency(self):
        return self.device.frequency

    def read_reference(self):
        ref = self.device.reference
        if ref == 'internal':
            return 0
        elif ref == 'external rear':
            return 1
        elif ref == 'external front':
            return 2

    def read_ACcoupling(self):
        cou = self.device.coupling
        if cou == 1.0:
            return True
        else:
            return False

    def read_ground(self):
        cou = self.device.ground
        if cou == 1.0:
            return True
        else:
            return False

    ### WRITE COMMANDS ###

    def write_timeconstant(self,value):
        self.device.time_constant = self.device.TIME_CONSTANTS[value]

    def write_sensitivity(self,value):
        self.device.sensitivity = self.device.SENSITIVITIES[value]
        
    def write_gain(self,value):
        self.device.gain = self.GAINS[value]
    
    def write_slope(self, value):
        self.device.slope = self.SLOPES[value]
    
    def write_frequency(self, value):
        self.device.frequency = value

    def write_reference(self, value):
        self.device.reference = self.device.REFERENCES[value]

    def write_ACcoupling(self, value):
        if value:
            self.device.coupling = 1
        else:  
            self.device.coupling = 0

    def write_ground(self, value):
        if value:
            self.device.ground = 1
        else:  
            self.device.ground = 0

if __name__ == "__main__":
    DSP7265.run_server()

