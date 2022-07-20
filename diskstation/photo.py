import os
import exif

# photo class
class Photo(object):
    def __init__(self, id, name, title, latitude, longitude, gps_lat, gps_lng):
        self.id = id
        self.name = name
        self.title = title
        self.latitude = self.__casted_value_or_default__(latitude, None, float)
        self.longitude = self.__casted_value_or_default__(longitude, None, float)
        self.gps_lat = self.__casted_value_or_default__(gps_lat, None, float)
        self.gps_lng = self.__casted_value_or_default__(gps_lng, None, float)

    def __str__(self):
        return f"{self.name} <{self.id}>"

    def __casted_value_or_default__(self, value, default, cast):
        try:
            return cast(value)
        except:
            return default

    def __gps_decimal_coords__(self, coords, ref):
        decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
        if ref == 'S' or ref == 'W':
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def gps_from_file(self, basepath, precision=6):
        path = os.path.join(basepath, self.name)
        with open(path, 'rb') as img_file:
            img = exif.Image(img_file)
        if img.has_exif:
            img_exif_properties = img.list_all()
            if 'gps_latitude' in img_exif_properties \
                    and 'gps_longitude' in img_exif_properties \
                    and 'gps_latitude_ref' in img_exif_properties \
                    and 'gps_longitude_ref' in img_exif_properties:
                latitude = self.__gps_decimal_coords__(img.gps_latitude, img.gps_latitude_ref)
                longitude = self.__gps_decimal_coords__(img.gps_longitude, img.gps_longitude_ref)
                return (round(latitude, precision), round(longitude, precision))
        return (None, None)

    def to_deg(self, value, loc):
        """convert decimal coordinates into degrees, munutes and seconds tuple
        Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
        return: tuple like (25, 13, 48.343 ,'N')
        """
        if value < 0:
            loc_value = loc[0]
        elif value > 0:
            loc_value = loc[1]
        else:
            loc_value = ""
        abs_value = abs(value)
        deg = int(abs_value)
        t1 = (abs_value - deg) * 60
        min = int(t1)
        sec = round((t1 - min) * 60, 5)
        return (deg, min, sec, loc_value)

    def set_gps_location(self, file_name, lat, lng, altitude=0):
        """Adds GPS position as EXIF metadata
        Keyword arguments:
        file_name -- image file
        lat -- latitude (as float)
        lng -- longitude (as float)
        altitude -- altitude (as float)
        """
        if not str(file_name).upper().endswith("JPG"):
            return
        lat_deg = self.to_deg(lat, ["S", "N"])
        lng_deg = self.to_deg(lng, ["W", "E"])

        image_content = None
        with open(file_name, 'rb') as img_file:
            img = exif.Image(img_file)
            img.gps_latitude = lat_deg[:3]
            img.gps_latitude_ref = lat_deg[3]
            img.gps_longitude = lng_deg[:3]
            img.gps_longitude_ref = lng_deg[3]
            image_content = img.get_file()
        if image_content:
            with open(file_name, 'wb') as updated_img_file:
                updated_img_file.write(image_content)

    def gps_to_file(self, basepath, latitude, longitude):
        path = os.path.join(basepath, self.name)
        return self.set_gps_location(file_name=path, lat=latitude, lng=longitude)

if __name__ == "__main__":
    p = Photo(id="IMG_20181231_144810_xyz",
              name="IMG_20181231_144810.jpg",
              title="IMG_20181231_144810",
              latitude=None,
              longitude=None,
              gps_lat=None,
              gps_lng=None)
    print(p)
    (latitude, longitude) = p.gps_from_file(basepath="..\\samples\\camera_gps")
    print( (latitude, longitude) )
    p.gps_to_file(basepath="..\\samples\\camera_gps", latitude=latitude+0.000001, longitude=longitude+0.000001)
    (latitude, longitude) = p.gps_from_file(basepath="..\\samples\\camera_gps")
    print( (latitude, longitude) )
