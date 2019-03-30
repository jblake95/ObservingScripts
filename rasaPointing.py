"""
RASA pointing generator
- determine appropriate pointing for a desired norad id
- offset by half a FOV for maximum coverage
"""

from tle import (
    ST, 
    TLE,
    )
import json
import argparse as ap
from datetime import datetime
from astropy.table import Table

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

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
    
    parser.add_argument('tle_path',
                        help='path to json file containing tle info',
                        type=str)
    
    parser.add_argument('norad_id',
                        help='norad id of object to be observed',
                        type=str)
    
    parser.add_argument('--line1',
                        help='manually provide TLE line 1 to skip ST',
                        action='store_true')
    
    parser.add_argument('--line2',
                        help='manually provide TLE line 2 to skip ST',
                        action='store_true')
    
    return parser.parse_args()

if __name__ == "__main__":
	
	args = argParse()
	
	# check for log file
	try:
		tles = json.loads(args.tle_path)
	except:
		print('No tle file found. Initiating...')
		tles = {}
		with open(args.tle_path, 'w') as f:
			json.dumps(tles, f)
	
	# obtain relevant tle
	if args.line1 and args.line2:
		print('Using TLE provided...')
		tle = TLE(args.line1, args.line2)
	else:
		print('Pulling latest TLE from SpaceTrack...')
		st = ST()
		tle = st.getLatestTLE(args.norad_id)
		
	print(tle.line1, tle.line2, tle.name)
