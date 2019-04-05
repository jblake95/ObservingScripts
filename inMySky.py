"""
Find which satellites are visible at a given epoch and location
"""

from tle import (
    ST,
    TLE,
    SatCat,
    Orbit,
    )
import numpy as np
import argparse as ap
from datetime import datetime
from astropy.time import Time
from astropy import units as u
from astropy.table import Table
from astropy.coordinates import EarthLocation
from skyfield.api import utc
import matplotlib.pyplot as plt

# altitude limit for visibility
ALT_LIM = 30.*u.deg

# location of RASA, La Palma
SITE_LATITUDE = 28.7603135
SITE_LONGITUDE = -17.8796168
SITE_ELEVATION = 2387
SITE_LOCATION = EarthLocation(lat=SITE_LATITUDE*u.deg,
                              lon=SITE_LONGITUDE*u.deg,
                              height=SITE_ELEVATION*u.m)

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
    
    parser.add_argument('out_dir',
                        help='output directory for catalog',
                        type=str)
    
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

def onpick(event):
    """
    Actions to perform upon picker event
    
    Parameters
    ----------
    event : Picker event
        User picked a point
    """
    ind = event.ind
    obj = cat_info[ind]
    print('---------------------\n'
          'Selected object:\n'
          'Name:   {}\n'
          'ID:     {}\n'
          'Type:   {}\n'
          'Nation: {}\n'
          'Size:   {}\n'
          'Launch: {}\n'
          'Alt:    {}\n'
          'Incl:   {}\n'
          '---------------------'.format(obj['name'][0],
                                         obj['norad_id'][0],
                                         obj['type'][0],
                                         obj['country'][0],
                                         obj['size'][0],
                                         obj['launch'][0],
                                         obj['altitude'][0],
                                         obj['inclination'][0]))

if __name__ == "__main__":
    
    args = argParse()
    
    orbit, epoch = parseInput(args)
    
    # connect to Space-Track & pull catalog of TLEs
    st = ST()
    
    catalog = st.getLatestCatalog(orbit)
    print('Number of objects retrieved: {}'.format(str(len(catalog))))
    
    # filter out objects that aren't visible
    remove_keys = []
    for dummy, norad_id in enumerate(catalog.keys()):
        print('Checking {}/{}'.format(str(dummy),
                                      str(len(catalog))), end="\r")
        alt, _ = catalog[norad_id].altaz(epoch)
        if alt < ALT_LIM:
            remove_keys.append(norad_id)
    for norad_id in remove_keys:
        del catalog[norad_id]
    
    print('Number of objects visible: {}'.format(str(len(catalog))))
    
    # pull satcat and save relevant info to file
    global cat_info
    cat_info = Table(names=['norad_id', 
                            'name', 
                            'type',
                            'country',
                            'size',
                            'launch',
                            'altitude',
                            'ra',
                            'dec',
                            'period',
                            'apogee',
                            'perigee',
                            'inclination',
                            'eccentricity'],
                     dtype=['i8'] + ['U25']*5 + ['f8']*8)
    
    satcat = st.getSatCat(sorted(catalog.keys()))
    for i, norad_id in enumerate(sorted(catalog.keys())):
        print('Saving info {}/{}'.format(str(i),
                                         str(len(catalog))), end="\r")
        tle = catalog[norad_id]
        satcat_i = SatCat(satcat[i])
        cat_info.add_row([satcat_i.norad_id,
                          satcat_i.name,
                          satcat_i.objtype,
                          satcat_i.country,
                          satcat_i.size,
                          satcat_i.launchdate,
                          tle.altaz(epoch)[0].deg,
                          tle.radec(epoch)[0].deg,
                          tle.radec(epoch)[1].deg,
                          satcat_i.period,
                          satcat_i.apogee,
                          satcat_i.perigee,
                          tle.inclination,
                          tle.eccentricity])
    
    out_path = '{}InSky-{}-{}.csv'.format(args.out_dir,
                                          orbit.type,
                                          str(epoch).replace(' ', 'T'))
    cat_info.write(out_path, format='csv')
    
    # plot the visible objects and allow user to select & view info
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(cat_info['ra'], 
            cat_info['dec'], 
            'ko', 
            label='Objects', 
            picker=5)
    
    lst = Time(epoch, 
               scale='utc', 
               location=SITE_LOCATION).sidereal_time('apparent').deg
    ax.axvline(x=lst, 
               color='r', 
               linestyle='--', 
               label='LST')
    
    ax.set_xlabel('Right ascension [deg]')
    ax.set_ylabel('Declination [deg]')
    
    plt.legend()
    
    fig.canvas.mpl_connect('pick_event', onpick)
    
    plt.show()
