"""
Module for dealing with two-line element sets
"""

import getpass as gp
from spacetrack import SpaceTrackClient
from skyfield.sgp4lib import EarthSatellite
from skyfield.api import (
    load, 
    Topos,
    )
from astropy import units as u
from astropy.coordinates import Longitude, Latitude

TS = load.timescale() # save repeated use in iterative loops
LE_FORMAT = '3le'

SITE_LATITUDE = 28.7603135
SITE_LONGITUDE = -17.8796168
SITE_ELEVATION = 2387
TOPOS_LOCATION = Topos(SITE_LATITUDE, 
                       SITE_LONGITUDE, 
                       elevation_m=SITE_ELEVATION) # location of RASA

GEO_CHECK = ['g', 'geo']
LEO_CHECK = ['l', 'leo']
MEO_CHECK = ['m', 'meo']
HEO_CHECK = ['h', 'heo']
ALL_CHECK = ['a', 'all']

class ST:
    """
    Space-Track Interface
    """
    def __init__(self):
        un, pw = self.requestAccess()
        self.username = un
        self.password = pw
        self.client = SpaceTrackClient(identity=un, password=pw)
    
    def requestAccess(self):
        """
        Obtain user access details
        """
        st_un = 'J.Blake@warwick.ac.uk'
        st_pw = gp.getpass('Space-Track password: ')
        
        return st_un, st_pw
    
    def getLatestTLE(self, norad_id):
        """
        Obtain latest TLE for a NORAD object
        """
        elset = self.client.tle_latest(norad_cat_id=norad_id,
                                       iter_lines=True,
                                       ordinal=1,
                                       format=LE_FORMAT)
        tle = [line for line in elset]
        
        return TLE(tle[1], tle[2], name=tle[0])
    
    def getLatestCatalog(self, orb):
		"""
		Obtain latest TLE catalog for an orbital type
		"""
		if orb.type in GEO_CHECK + LEO_CHECK:
			result = self.client.tle(iter_lines=True,
									 eccentricity=orb.e_lim,
									 mean_motion=orb.mm_lim,
									 epoch='>now-30',
									 ordinal=1,
									 limit=200000,
									 format=LE_FORMAT)
		elif orb.type in MEO_CHECK:
			result = self.client.tle(iter_lines=True,
									 eccentricity=orb.e_lim,
									 period=orb.p_lim,
									 epoch='>now-30',
									 ordinal=1,
									 limit=200000,
									 format=LE_FORMAT)
		elif orb.type in HEO_CHECK:
			result = self.client.tle(iter_lines=True,
									 eccentricity=orb.e_lim,
									 epoch='>now-30',
									 ordinal=1,
									 limit=200000,
									 format=LE_FORMAT)
		elif orb.type in ALL_CHECK:
			result = self.client.tle(iter_lines=True,
									 epoch='>now-30',
									 ordinal=1,
									 limit=200000,
									 format=LE_FORMAT)
		else:
			print('Incorrect format! Please supply a valid' 
				  'orbit type... \n'
				  'GEO - "g" \n'
				  'LEO - "l" \n'
				  'MEO - "m" \n'
				  'HEO - "h" \n'
				  'ALL - "a" \n')
			quit()
		
		#TODO: organize into user-friendly format
		
		return catalog

class TLE:
    """
    Two Line Element
    """
    def __init__(self, line1, line2, name=None):
        self.line1 = line1
        self.line2 = line2
        if name is not None:
            self.name = name[2:]
        
        # ephemeris info
        self.obs = TOPOS_LOCATION
        self.obj = EarthSatellite(line1, line2, name)
        self.ts = TS
        
        # book-keeping
        self.norad_id = int(self.line1[2:7])
        self.yday = float(self.line1[20:32])
        
        # orbital properties
        self.inclination = float(self.line2[8:16])
        self.eccentricity = float(self.line2[26:33])
        self.raan = float(self.line2[17:25])
        self.argperigree = float(self.line2[34:42])
        self.mean_anomaly = float(self.line2[43:51])
        self.mean_motion = float(self.line2[52:63])
    
    def radec(self, epoch):
        """
        Determine radec coords for a given epoch
        """
        ra, dec, _ = (self.obj-self.obs).at(self.ts.utc(epoch)).radec()
        
        return Longitude(ra.hours, u.hourangle), Latitude(dec.degrees, u.deg)

class Orbit:
    """
    Convenience class for orbit-specific searches
    """
    def __init__(self, orb_type):
        """
        Initiate Orbit object using SpaceTrack definitions
        
        Parameters
        ----------
        orb_type : str
            Desired type of orbit
            'g' - GEO
            'l' - LEO
            'm' - MEO
            'h' - HEO
            'a' - ALL
        """
        self.type = orb_type.lower()
        if self.type in GEO_CHECK:
            self.e_lim = '<0.01'
            self.mm_lim = '0.99--1.01'
        elif self.type in LEO_CHECK:
            self.e_lim = '<0.25'
            self.mm_lim = '>11.25'
        elif self.type in MEO_CHECK:
            self.e_lim = '<0.25'
            self.p_lim = '600--800'
        elif self.type in HEO_CHECK:
            self.e_lim = '>0.25'
        elif self.type in ALL_CHECK:
            print('Full catalogue specified; no limits placed.')
        else:
            print('Incorrect format! Please provide a valid' 
                  'orbit type... \n'
                  'GEO - "g" \n'
                  'LEO - "l" \n'
                  'MEO - "m" \n'
                  'HEO - "h" \n'
                  'ALL - "a" \n')
            quit()
