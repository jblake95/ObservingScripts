"""
Script to convert angular units
"""

import argparse as ap
from astropy.coordinates import Angle
from astropy import units as u

def argParse():
    """
    Argument parser settings
    
    Parameters
    ----------
    None
    
    Returns
    -------
    args : array-like
        Array of command line arguments
    
    Raises
    ------
    None
    """
    
    parser = ap.ArgumentParser()
    
    parser.add_argument('angle',
                        help='angle to be converted',
                        type=str)
    
    parser.add_argument('--rad2deg',
                        help='radians to degrees',
                        action='store_true')
    
    parser.add_argument('--deg2rad',
                        help='degrees to radians',
                        action='store_true')
    
    parser.add_argument('--dec2sexagesimal',
                        help='declination in degrees to sexagesimal',
                        action='store_true')
    
    parser.add_argument('--dec2deg',
                        help='declination in sexagesimal to degrees',
                        action='store_true')
    
    parser.add_argument('--ra2sexagesimal',
                        help='right ascension in degrees to sexagesimal',
                        action='store_true')
    
    parser.add_argument('--ra2deg',
                        help='right ascension in sexagesimal to degrees',
                        action='store_true')
    
    parser.add_argument('--ra2ha',
                        help='right ascension to current hour angle',
                        action='store_true')
    
    parser.add_argument('--ha2ra',
                        help='hour angle to current right ascension',
                        action='store_true')
    
    return parser.parse_args()

def rad2deg(angle):
    """
    convert radians to degrees
    """
    angle_rad = Angle(angle, u.rad)
    
    return angle_rad.deg

def deg2rad(angle):
    """
    convert degrees to radians
    """
    angle_deg = Angle(angle, u.deg)
    
    return angle_deg.rad

def dec2sexagesimal(angle):
    """
    convert declination in degrees to sexagesimal format
    """
    angle_deg = Angle(angle, u.deg)
    
    return angle_deg.to_string()

def dec2deg(angle):
    """
    convert declination in sexagesimal format to degrees
    """
    angle_deg = Angle(angle, u.deg)
    
    return angle_deg

def ra2sexagesimal(angle):
    """
    convert a right ascension in degrees to sexagesimal format
    """
    angle_deg = Angle(angle, u.deg)
    angle_hourangle = Angle(angle.hourangle, u.hourangle)
    
    return angle_hourangle.to_string(), angle_hourangle

def ra2deg(angle):
    """
    convert a right ascension in sexagesimal format to degrees
    """
    angle_sexagesimal = Angle(angle, u.hourangle)
    
    return angle_sexagesimal.deg

def main(args):
    """
    Carry out requested conversion
    """
    
    if args.rad2deg:
        print('Angle in degrees: ', rad2deg(args.angle))
    
    elif args.deg2rad:
        print('Angle in radians: ', deg2rad(args.angle))
    
    elif args.dec2sexagesimal:
        print('Declination in sexagesimal format: ')
    
    return None

if __name__ == "__main__":
    
    args = argParse()
    
    main(args)
