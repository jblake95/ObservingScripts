"""
Find which satellites are visible at a given epoch and location
"""

from tle import (
    ST,
    TLE,
    Orbit,
    )
import argparse as ap
from datetime import datetime
from astropy import units as u
from skyfield.api import utc
import matplotlib.pyplot as plt

ALT_LIM = 30.*u.deg

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
    """
    parser = ap.ArgumentParser()
    
    parser.add_argument('--orbit',
                        help='type of orbit',
                        type=str)
    
    parser.add_argument('--epoch',
                        help='epoch for propagating TLEs, \n'
                             'format: YYYY-mm-ddTHH:MM:SS.s [utc]',
                        type=str)
    
    return parser.parse_args()

def parseInput(args):
    """
    Parse user-input arguments in a more useful format
    
    Parameters
    ----------
    args : argparse object
        Arguments returned by argparse user interaction
    
    Returns
    -------
    orbit : Orbit object
        Orbit object encoding desired orbital type
    epoch : datetime object
        datetime object [utc] with replaced tzinfo as utc
    """
    if args.orbit:
        orbit = Orbit(args.orbit)
    else:
        orbit = Orbit('all')
    
    if args.epoch:
        print('***WARNING: TLE loses accuracy over time!***')
        epoch = datetime.strptime(args.epoch, 
                                  '%Y-%m-%dT%H:%M:%S.%f')
        epoch = epoch.replace(tzinfo=utc)
    else:
        epoch = datetime.utcnow().replace(tzinfo=utc)
    
    return orbit, epoch

if __name__ == "__main__":
    
    args = argParse()
    
    orbit, epoch = parseInput(args)
    
    # connect to Space-Track & pull TLEs
    st = ST()
    
    catalog = st.getLatestCatalog(orbit)
    print('Number of objects retrieved: {}'.format(str(len(catalog))))
    
    # filter out objects that aren't visible
    remove_keys = []
    for norad_id in catalog.keys():
        alt, _ = catalog[norad_id].altaz(epoch)
        if alt < ALT_LIM:
            remove_keys.append(norad_id)
    
    for norad_id in remove_keys:
        del catalog[norad_id]
    
    print('Number of objects visible: {}'.format(str(len(catalog))))
        
        
        
