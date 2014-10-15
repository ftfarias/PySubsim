from util import Bands

KNOWN_TYPES = {
    # Symbol for map display
    # Number of blades. ex: [4,5] four or five blades.
    # Sonar Bands
    # bands:  50, 100, 300, 500, 1000, 2000, 15000, 20000

    # f = 12 Hz - @2-5 kHz for “whale songs”, SL up to 188 dB
    'Whale': {'symbol': 'B',
         'blades': [0, 0],
         'bands': Bands(),
         'noise': [50, 80],
         'deep': [0, 100]},

    # generate intense broadband noise, f = 1-10 kHz, SL =60-90 dB
    'Snapping Shrimp': {'symbol': 'B',
         'blades': [0, 0],
         'bands': Bands(),
         'noise': [80, 100],
         'deep': [10, 15]},


    # Merchant Vessels/Tankers: Typically three or four blades; noisy;
    # often maintains predictable course.
    'Large Merchant Vessel':
        {'symbol': 'M',
         'blades': [3, 4],
         'bands': Bands(),
         'noise': [80, 90],
         'deep': [0, 0]},

    'Small Merchant Vessel':
        {'symbol': 'M',
         'blades': [3, 4],
         'bands': Bands(),
         'noise': [70, 80],
         'deep': [0, 0]},

    # Warships: Typically four or five-bladed propellers; quieter, smoother
    # sound than merchant ships; possibly unpredictable course changes.

    'Destroyer':
        {'symbol': '^',
         'blades': [4, 5],
         'bands': Bands(),
         'noise': [60, 70],
         'deep': [0, 0]},

    'Warship':
        {'symbol': '^',
         'blades': [4, 5],
         'bands': Bands(),
         'noise': [75, 85],
         'deep': [0, 0]},

    # Submarines: Five, six or seven-bladed propellers;
    # very quiet when submerged and at low speed; unpredictable course changes.
    'Akula':
        {'symbol': 'S',
         'blades': [7, 7],
         'bands': Bands(),
         'noise': [55, 75],
         'deep': [68, 300]},

    '688':
        {'symbol': 'S',
         'blades': [6, 6],
         'bands': Bands(),
         'noise': [50, 70],
         'deep': [68, 300]},

    # Fishing Vessels/Trawlers/Pleasure Craft: Three- or four-bladed propellers;
    # noisy; erratic courses and speeds, frequently stopping and starting.

    'Fishing Boat':
        {'symbol': 'F',
         'blades': [3, 4],
         'bands': Bands(),
         'noise': [80, 90],
         'deep': [0, 0]},

    'Fishing Ship':
        {'symbol': 'F',
         'blades': [3, 4],
         'bands': Bands(),
         'noise': [55, 65],
         'deep': [0, 0]},

    'Torpedo':
        {'symbol': 'T',
         'blades': [5, 5],
         'bands': Bands([20000]),
         'noise': [110, 110],
         'deep': [0, 0]},

}