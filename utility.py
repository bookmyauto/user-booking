from math import sin, cos, sqrt, atan2, radians


class Utility:
    
    # computes distance between two coordinates
    @staticmethod
    def distance(f_lat, f_lon, t_lat, t_lon):
        R = 6373.0
        lat1 = radians(f_lat)
        lon1 = radians(f_lon)
        lat2 = radians(t_lat)
        lon2 = radians(t_lon)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        return distance

    # sort drivers based on their distances from user
    @staticmethod
    def sort_drivers(curr_lat, curr_long, data):
        try:
            curr_long       = float(curr_long)
            curr_lat        = float(curr_lat)
            driver_distance = []
            for row in data:
                driver_id   = row[0]
                lat         = float(row[1])
                lon         = float(row[2])
                dist        = Utility.distance(lat, lon,  curr_lat, curr_long)
                if dist > 0:
                    driver_distance.extend([[driver_id, dist]])
            if len(driver_distance) > 0:
                driver_distance.sort(key = lambda x: x[1])
            return driver_distance, 1
        except Exception as e:
            print("Error in sort drivers: " + str(e))
            return [], 0
