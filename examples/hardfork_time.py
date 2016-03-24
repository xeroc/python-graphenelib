import time
import datetime

# Now
dtime = datetime.datetime.now()

# Add delay
# class datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
dtime = dtime + datetime.timedelta(0, 60 * 60 * 12)

# print timestamp
print(int(time.mktime(dtime.timetuple())))
