


class TowerArray(object):
    TOWED_ARRAY_DEPLOY_SPEED = 100 * 60  # 300 feet per minute

    def __init__(self):
        self.description = 'generic towed array'



class TD16DTowedArray(TowerArray):
    TOTAL_LENGTH = 2400 + 240
    """ 
    TB-16 Fat Line Towed Array

    The TB-16 Fat Line Towed Array consists of a 1400 pound 
      accoustic detector array, some 3.5 inches in diameter and 240 feet long, towed on a
      2,400 foot long cable 0.37 inches in diameter weighing 450 pounds.

    Medium range 
    low-frequency
    2600 foot 3.5 inches/ 89mm thick
    hydrophones in the last 240 foot
    
    max distance: 18.000 yards / 9.1 NM
    """

    def __init__(self):
        self.description = 'TB-16 Fat Line Towed Array'


"""

####  Spherical Sonar:

max distance: 14.000 yards / 6.9 NM


AN/BQQ-5[edit]
AN/BQQ-5 sensor suite consists of the AN/BQS-13 spherical sonar array 
and AN/UYK-44 computer. The AN/BQQ-5 was developed from the AN/BQQ-2 sonar system.
 The BQS 11, 12, and 13 spherical arrays have 1,241 transducers.
  Also equipped are a 104 hydrophone hull array and two towed arrays:
   the TB-12 (later replaced by the TB-16) and TB-23 or TB-29, of
    which there are multiple variants. There are 5 versions of the AN/BQQ-5 system,
     sequentially identified by letters A-E.

The 688i (Improved) subclass was initially equipped with the AN/BSY-1 SUBACS 
submarine advanced combat system that used an AN/BQQ-5E sensor system with 
updated computers and interface equipment. Development of the AN/BSY-1 and its 
sister the AN/BSY-2 for the Seawolf class was widely reported as one of the 
most problematic programs for the Navy, its cost and schedule suffering many setbacks.

A series of conformal passive hydrophones are hard-mounted 
to each side of the hull, using the AN/BQR-24 internal processor. The
 system uses FLIT (frequency line integration tracking) which homes 
 in on precise narrowband frequencies of sound and, using the Doppler principle,
  can accurately provide firing solutions against very quiet submarines. 
  The AN/BQQ-5’s hull array doubled the performance of its predecessors.

AN/BQQ-10[edit]
The AN/BQQ-5 system was replaced by the AN/BQQ-10 system.
 Acoustic Rapid Commercial Off-The-Shelf Insertion (A-RCI), 
 designated AN/BQQ-10, is a four-phase program for transforming existing 
 submarine sonar systems (AN/BSY-1, AN/BQQ-5, and AN/BQQ-6) from legacy systems
  to a more capable and flexible COTS/Open System Architecture (OSA) and also 
  provide the submarine force with a common sonar system. A single A-RCI
   Multi-Purpose Processor (MPP) has as much computing power as the entire 
   Los Angeles (SSN-688/688I) submarine fleet combined and will allow 
   the development and use of complex algorithms previously beyond the 
   reach of legacy processors. The use of COTS/OSA technologies and systems
    will enable rapid periodic updates to both software and hardware. 
    COTS-based processors will allow computer power growth at a rate 
    commensurate with the commercial industry.[21]


##  TD-16D 


## TD-23
Passive thin-line
1.1 inches/28mm
960 foot of hydrophones
very low frequency at very long range
Heading sensor:
- Resolution : 0.3o
- Accuracy: 0.5o
- Pitch: +/- 15o
Depth Sensor: 
- Resolution : 0.5 meters
- Accuracy: 1.0 meters
- Range: 800 m
Temperature:
- Resolution : 0.3 oC
- Accuracy: 0.5 oC


Specifications
 
Maximum operating depth
800 m
Survival depth
1500 m
Temperature
Operating: -2.5°C to 40°C Storage: -40°C to 70°C Reeling: -10°C to 40°C
Frequency range
Configurable to customer requirements
Heading sensor
Resolution: 0.3° Accuracy: 0.5°
Roll Output: Continuous Pitch: ±15°
Depth sensor
Resolution: 0.5 m (1.64 ft) Accuracy: 1.0 m (3.28 ft) Range: 800 m (2,625 ft)
Temperature sensor
Resolution: 0.3°C Accuracy: 0.5°C

L-3 Ocean Systems
Submarine Towed Arrays
• TB-16F – The latest fatline array with heading sensors
• TB-23 – The standard thinline array with improvements
• TB-29A – The new thinline array being developed by the Omnibus program


WLR-9 
Active sonar detector


# HS-100
The HS-100 is a compact, long-range, multifunction hull-mounted sonar. Decades of dipping sonar
 experience and expertise have resulted in this slimmed down, dome profile which conforms to the
  hydrodynamic, low-drag bulbous bow shape of a surface warship.
The transducer elements of the HS-100 are constructed from PMN (lead magnesium niobate).
 The mid-frequency (MF) multiplexed hydrophone channels are easily interfaced to an open
  architecture COTS acoustic processor.
The HS-100 uses 32 modern projectors to provide the high source levels necessary
 for long-range detection. The vertical “line” transmit array design produces large
  time-bandwidth wave trains that are not possible with traditional sector scan sonars.
   The lightweight, receive volumetric array comprises a vertical set of receive hydrophone 
   staves with embedded ATM digital telemetry processing that eliminates the need for individual sensor cabling, transmit/receive switches and signal conditioning cabinets found in traditional active sonars.
The HS-100 is being developed by L-3 Communications Ocean Systems as a “green” sonar 
in that its transmissions do not harm aquatic life such as whales and dolphins


HS-100 Specifications
 
 
Application:
Requirement
Bow Dome
 
Keel Dome
Transmit horizontal beam width
360° / 107°
360° / 107°
Transmit vertical beam width
11° / 11°
21° / 21°
 
Transmit bandwidth
2.5 kHz to 4.5 kHz
Transmit source level
228 dB re 1 μPa @ 1 m
 
223 dB re 1 μPa @ 1 m
Transmit array height
92 in
56 in
Transmit array width/depth
22 in / 22 in
22 in / 22 in
 
Receive bandwidth (active)
1 kHz to 5 kHz
Receive bandwidth (passive)
800 Hz to 5.0 kHz
Receiver dynamic range
80 dB
Own ship Doppler nullification
30 kts
Doppler range
±36 kts
Operational speed
Up to 30 kts
Operational sea state
SS6
Operating modes
Active, Passive, Maintenance,Training
Tracking
Yes
Contact management
Yes
Outboard system weight
<2,000 lbs
Number of projector elements
64
Receive array diameter
72 in
 
60 in
Number of hydrophones (total)
576
 
360




####   HS-200

   The HS-200 combines HS-100, LFATS VDS-100 and latest transducer technologies
    to satisfy recent requirements for a low frequency (< 2 kHz), hull-mounted
     sonar retrofit into a 1.2-meter dome.
 HS-200 Specifications
 
Arrays
Height: 116 cm Diameter: 116 cm Weight: <500 kg
Operating modes
Active: (CW, FM, Combined CW/FM) with Torpedo Alert
Passive: (Narrowband, Broadband and DEMON) Playback
Maintenance Test Idle
Operating frequencies
Active: 1,800 – 2,300 Hz Passive: 1,000 – 4,500 Hz
Source Level
Omnidirectional = 215 dB re 1 μPa @ 1m Sector Directed = 217 dB re 1μPa @ 1m
Range scales
2,4,8,16,32 km
Transmit array
Number of channels – 16
(arrange in sour staves of four projectors)
Own Doppler nullification
0 – 30 kts
Processing
 
COTS Quad Power PCs (DY4)
"""