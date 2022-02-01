from datetime import datetime, timedelta

timezone_delta = {
    'GMT':	0,
    'UTC':	0,
    'ECT':	1,
    'EET':	2,
    'ART':	-3,
    'EAT':	3,
    'MET':	4,
    'NET':	4,
    'PLT':	5,
    'IST':	5.5,
    'BST':	6,
    'VST':	7,
    'CTT':	8,
    'JST':	9,
    'ACT':	9.5,
    'AET':	10,
    'SST':	11,
    'NST':	12,
    'MIT':	-11,
    'HST':	-10,
    'AST':	-9,
    'PST':	-8,
    'MST':	-7,
    'CST':	-6,
    'EST':	-5,
    'CNT':	-3.5
}


class TimeZoneConverter:
    def to_utc(self, start_datetime, timezone):
        hour_delta = timezone_delta[timezone]
        if hour_delta is None:
            raise ValueError("Invalid timezone format")

        check_int = isinstance(hour_delta, int)
        hour_delta = hour_delta * -1
        delta = None

        if check_int:
            delta = timedelta(hours=hour_delta)
        else:
            if hour_delta < 0:
                delta = timedelta(hours=int(hour), minutes=-30)
            else:
                delta = timedelta(hours=int(hour_delta), minutes=30)

        converted_time = start_datetime + delta
        #print("CONVERTED TIME: {}".format(converted_time))
        return converted_time
