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
LE_FORMAT = '3le'     # TODO: generalise to allow for 'tle' format

SITE_LATITUDE = 28.7603135
SITE_LONGITUDE = -17.8796168
SITE_ELEVATION = 2387
TOPOS_LOCATION = Topos(SITE_LATITUDE, 
                       SITE_LONGITUDE, 
                       elevation_m=SITE_ELEVATION)

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
