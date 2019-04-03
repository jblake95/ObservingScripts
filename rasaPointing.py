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
from datetime import datetime, timedelta
from skyfield.api import utc
from astropy import units as u
from astropy.coordinates import SkyCoord, Longitude, Latitude

SEP_LIMIT = 1.3*u.deg # separation limit ~ half RASA FOV

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

def getPointing(tle):
	"""
	Find a pointing that keeps the object of interest within the RASA
	FOV for as long as possible
	
	Parameters
	----------
	tle : TLE object
	    Object containing two line ephemeris information for the object
	    of interest
	
	Returns
	-------
	ra, dec : float
	    Right ascension and declination of desired pointing
	"""
	# propagate tle to current time
	epoch = datetime.now().replace(tzinfo=utc)
	ra_now, dec_now = tle.radec(epoch)
	coord_now = SkyCoord(ra_now, 
	                     dec_now, 
	                     unit=u.deg, 
	                     frame='icrs')
	print(ra_now, dec_now)
	# now propagate in 5s steps until FOV limit is reached
	d = 0*u.deg
	while True:
		epoch += timedelta(seconds=5)
		ra, dec = tle.radec(epoch)
		print(ra, dec)
		coord = SkyCoord(ra, 
		                 dec, 
		                 unit=u.deg, 
		                 frame='icrs')
		
		d = coord_now.separation(coord)
		if d < SEP_LIMIT:
			ra_pointing, dec_pointing = ra, dec
		else:
			break
	
	return ra_pointing, dec_pointing

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
	
	# find expected radec and offset by half FOV
	ra, dec = getPointing(tle)
	
	print('---------------------\n'
	      'Expected position of NORAD {}\n'
	      'RA:  {}\n'
	      'DEC: {}\n'
	      '---------------------'.format(str(args.norad_id),
	                                     ra.to_string(),
	                                     dec.to_string()))
