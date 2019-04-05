"""
Plot altitude of an object over a range of time
"""

from tle import TLE
from datetime import datetime, timedelta
from skyfield.api import utc
import matplotlib.pyplot as plt

tle = TLE('1  6275U 72089A   18140.63615366 +.00000033 +00000-0 +30486-4 0  9997',
          '2  6275 098.5286 350.5995 0035704 357.2475 002.8504 14.27778842363593',
          name='OPS 7323')

epoch = datetime.strptime('2018-05-20T20:50:00',
                          '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)
i=0
alts = []
times = []
while i < 200:
	alts.append(tle.altaz(epoch)[0].deg)
	times.append(epoch)
	
	epoch += timedelta(seconds=6)
	i += 1

plt.plot(times, alts, 'k.')

plt.title('Pass of NORAD ID 6275 (OPS 7323)')

plt.xlabel('Time [utc]')
plt.ylabel('Altitude [deg]')

plt.show()
