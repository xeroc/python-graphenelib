import time
import datetime

# Now
dtime = datetime.datetime.now()

# Add delay
# class datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
dtime = dtime + datetime.timedelta(60 * 60 * 2)

# print timestamp
print(time.mktime(dtime.timetuple()))
