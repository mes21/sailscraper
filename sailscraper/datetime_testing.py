from datetime import datetime as dt
from datetime import timedelta as delta



t1 = dt.strptime("2020-12-01", "%Y-%m-%d")


t2 = dt.strptime("2020-12-03", "%Y-%m-%d")


print((t2 - t1).days)