"""
Script to convert angular units
"""

import argparse as ap
from datetime import datetime
from astropy import units as u
from astropy.coordinates import (
    Angle,
    EarthLocation,
    )
from astropy.time import Time

SITE_LATITUDE = 28.761935*u.deg
SITE_LONGITUDE = -17.877591*u.deg
SITE_ELEVATION = 2348*u.m

SITE_LOCATION = EarthLocation(lat = SITE_LATITUDE,
                              lon = SITE_LONGITUDE,
                              height = SITE_ELEVATION)

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

def ra2ha(ra):
    """
    convert right ascension to hour angle at the current time
    """
    ra = Angle(ra, u.hourangle)
    
    utc_now = Time(datetime.utcnow(), scale='utc', location=SITE_LOCATION)
    lst = utc_now.sidereal_time('apparent')
    
    return (lst - ra).wrap_at(12*u.hourangle)

def ha2ra(ha):
    """
    convert hour angle to right ascension at the current time
    """
    ha = Angle(ha, u.hourangle)
    
    utc_now = Time(datetime.utcnow(), scale='utc', location=SITE_LOCATION)
    lst = utc_now.sidereal_time('apparent')
    
    return (lst - ha).wrap_at(24*u.hourangle)

def main(args):
    """
    Carry out requested conversion
    """
    
    if args.rad2deg:
        print('Angle in degrees: ', rad2deg(args.angle))
    
    elif args.deg2rad:
        print('Angle in radians: ', deg2rad(args.angle))
    
    elif args.dec2sexagesimal:
        print('Declination in sexagesimal format: ', dec2sexagesimal(args.angle))
    
    elif args.dec2deg:
        print('Declination in degrees: ', dec2deg(args.angle))
    
    elif args.ra2sexagesimal:
        print('Right ascension in sexagesimal format: ', ra2sexagesimal(args.angle))
    
    elif args.ra2deg:
        print('Right ascension in degrees: ', ra2deg(args.angle))
    
    elif args.ra2ha:
        print('Hour angle: ', ra2ha(args.angle))
    
    elif args.ha2ra:
        print('Right ascension: ', ha2ra(args.angle))
    
    return None

if __name__ == "__main__":
    
    args = argParse()
    
    main(args)
