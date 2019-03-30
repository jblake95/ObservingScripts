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
    
    parser.add_argument('log_path',
                        help='path to json file containing tle log',
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
		with open(args.log_path, 'r') as f:
			log = json.load(f)
	except:
		print('No log file found. Initiating...')
		log = {}
	
	# if not provided manually, obtain latest tle from Space-Track
	if args.line1 and args.line2:
		print('Using TLE provided...')
		tle = TLE(args.line1, args.line2)
	else:
		print('Pulling latest TLE from SpaceTrack...')
		st = ST()
		tle = st.getLatestTLE(args.norad_id)
	
	# logging if TLE is new
	if args.norad_id in log.keys():
		old_tle = TLE(log[args.norad_id][-1][0],
		              log[args.norad_id][-1][1])
		if tle.yday != old_tle.yday:
			log[args.norad_id].append([tle.line1,
			                           tle.line2])
		with open(args.log_path, 'w') as f:
			json.dump(log, f)
	else:
		log.update({args.norad_id:[]})
		log[args.norad_id].append([tle.line1,
			                       tle.line2])
		print(log)
		with open(args.log_path, 'w') as f:
			json.dump(log, f)
	
	# find expected radec
	ra, dec = tle.radec(datetime.now().replace(tzinfo=utc))
	
	print('---------------------\n'
	      'Expected position of NORAD {}\n'
	      'RA:  {}\n'
	      'DEC: {}\n'
	      '---------------------'.format(str(args.norad_id),
	                                     ra.to_string(),
	                                     dec.to_string()))
