"""
RASA pointing generator
- determine appropriate pointing for a desired norad id
- offset by half a FOV for maximal and efficient coverage
- log the TLEs used throughout night
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
#SIDEREAL_RATE = 

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
                        help='manually provide TLE line 1 to bypass ST',
                        action='store_true')
    
    parser.add_argument('--line2',
                        help='manually provide TLE line 2 to bypass ST',
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
	    Right ascension and declination of desired pointing giving 
	    maximal coverage
	"""
	# propagate tle to current time
	epoch_now = datetime.utcnow().replace(tzinfo=utc)
	ra_now, dec_now = tle.radec(epoch_now)
	coord_now = SkyCoord(ra_now, 
	                     dec_now, 
	                     unit=u.deg, 
	                     frame='icrs')
	
	print('---------------------\n'
	      'Position of NORAD {} at {}\n'
	      'RA:  {}\n'
	      'DEC: {}\n'
	      '---------------------'.format(str(tle.norad_id),
	                                     str(epoch_now),
	                                     ra_now.to_string(),
	                                     dec_now.to_string()))
	
	# propagate tle ahead in 5s steps until FOV limit is reached
	delta_t = 5
	d = 0*u.deg
	while True:
		epoch = epoch_now + timedelta(seconds=delta_t)
		ra, dec = tle.radec(epoch)
		
		coord = SkyCoord(ra, 
		                 dec, 
		                 unit=u.deg, 
		                 frame='icrs')
		d = coord_now.separation(coord)
		
		if d < SEP_LIMIT:
			ra_pointing, dec_pointing = ra, dec
			# offset not worth it for high delta_t
			if delta_t > 1800:
				print('Exceeded 1hr without leaving FOV.\n'
				      'Using original pointing...')
				ra_pointing, dec_pointing = ra_now, dec_now
		# warn user if object within FOV for short time
		elif d > SEP_LIMIT and delta_t < 30:
			print('FOV limit reached.\n'
			      '***WARNING: Less than 1min within FOV!***')
			break
		else:
			print('FOV limit reached.')
			break
		
		delta_t += 5
	
	return ra_pointing, dec_pointing, delta_t

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
		
		with open(args.log_path, 'w') as f:
			json.dump(log, f)
	
	# find expected radec and offset by half FOV
	ra, dec, dt = getPointing(tle)
	
	print('---------------------\n'
	      'Position of NORAD {} in {}s\n'
	      'RA:  {}\n'
	      'DEC: {}\n'
	      '---------------------'.format(str(args.norad_id),
	                                     str(dt),
	                                     ra.to_string(),
	                                     dec.to_string()))
	
