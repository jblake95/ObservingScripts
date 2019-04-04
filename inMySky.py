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
from skyfield.api import utc

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
    
    parser.add_argument('--type',
                        help='type of orbit',
                        type=str)
    
    parser.add_argument('--epoch',
                        help='manually provide TLE line 1 to bypass ST',
                        action='store_true')
    
    return parser.parse_args()

if __name__ = "__main__":
	
	args = argParse()
	
	if args.type:
		orbit = Orbit(args.type)
	else:
		orbit = Orbit('all')
	
	# connect to Space-Track & pull TLEs
	st = ST()
	
	catalog = st.getLatestCatalog(orbit)
		
