import os
import math
import shutil
from pathlib import Path
from diskstation.auth import Auth
from diskstation.album import Album

# default values for all needed configuration variables
base_url = 'http://diskstationold/photo/webapi/'
base_file_location = r'C:\temp\photo_temp'
base_bad_file_location = os.path.join(base_file_location, r'.\..\bad_photo_temp')
username = ""
password = ""
# Try to replace the default values with the real ones by importing everything from the file 'conf.py'
# In 'conf.py' you just redefine all variables that you want to overwrite and assign them the real values
try:
    from .conf import *
except:
    print("No user specific configuration given, it is up to you to decide if this makes sense... continuing anyway")

auth = Auth(base_url=base_url, user=username, password=password)
auth.login()

i = 1
photos_to_process_manually = []
photos_without_file_coords = []
photos_file_coords_updated = []
good_photos = []
for album in Album.albums(base_url=base_url):
    print(f"{i}: {album}")
    i += 1
    photos = album.photos(base_url=base_url)
    for photo in photos:
        try:
            (file_latitude, file_longitude) = photo.gps_from_file(basepath=os.path.join(base_file_location, album.sharepath))
        except:
            continue
        NO_COORDS        = "NoPhotoCordinates   "
        NO_BACKUP_COORDS = "NoBackupCoordinates "
        NO_FILE_COORDS   = "NoFileCoordinates   "
        NO_COORD_MATCH   = "NoFullCoordinateMatch"
        findings = []
        file_coords_given = True
        photo_coords_given = True
        backup_coords_given = True
        if file_longitude in [None, 0.0] or file_latitude in [None, 0.0]:
            file_coords_given = False
            findings.append(NO_FILE_COORDS)
            photos_without_file_coords.append(f"{''.join(findings)} {album.sharepath} -> {photo.name} -> lat {photo.latitude}-{photo.gps_lat}-{file_latitude} / lng {photo.longitude}-{photo.gps_lng}-{file_longitude}")
        if photo.longitude in [None, 0.0] or photo.latitude in [None, 0.0]:
            photo_coords_given = False
            findings.append(NO_COORDS)
        if photo.gps_lng in [None, 0.0] or photo.gps_lat in [None, 0.0]:
            backup_coords_given = False
            findings.append(NO_BACKUP_COORDS)
        if not len(findings):  # this condition makes sure that all coordinates are non None or 0.0
            if math.isclose(photo.longitude, photo.gps_lng, rel_tol=0.000005) \
                    and math.isclose(photo.latitude, photo.gps_lat, rel_tol=0.000005) \
                    and math.isclose(photo.longitude, file_longitude, rel_tol=0.000005) \
                    and math.isclose(photo.latitude, file_latitude, rel_tol=0.000005):
                good_photos.append(f"{album.sharepath} -> {photo.name} -> lat {photo.latitude}-{photo.gps_lat} / lng {photo.longitude}-{photo.gps_lng}")
            else:
                findings.append(NO_COORD_MATCH)
        if not file_coords_given and (photo_coords_given or backup_coords_given):
            if photo_coords_given:
                latitude = photo.latitude
                longitude = photo.longitude
            else:
                latitude = photo.gps_lat
                longitude = photo.gps_lng
            #Write this to file
            try:
                photo.gps_to_file(basepath=os.path.join(base_file_location, album.sharepath), latitude=latitude, longitude=longitude)
                photos_file_coords_updated.append(f"{''.join(findings)} {album.sharepath} -> {photo.name} -> lat {photo.latitude}-{photo.gps_lat}-{file_latitude} / lng {photo.longitude}-{photo.gps_lng}-{file_longitude}")
            except Exception as e:
                print("Ups... " + repr(e))
                raise
        if len(findings):
            print(f"{''.join(findings)} {photo.name} -> lat {photo.latitude}-{photo.gps_lat}-{file_latitude} / lng {photo.longitude}-{photo.gps_lng}-{file_longitude}")
            photos_to_process_manually.append(f"{''.join(findings)} {album.sharepath} -> {photo.name} -> lat {photo.latitude}-{photo.gps_lat}-{file_latitude} / lng {photo.longitude}-{photo.gps_lng}-{file_longitude}")
            # copy the photo to the bad bank file location
            Path(os.path.join(base_bad_file_location, album.sharepath)).mkdir(parents=True, exist_ok=True)  # create directory
            src = os.path.join(base_file_location, album.sharepath, photo.name)
            dest = os.path.join(base_bad_file_location, album.sharepath, photo.name)
            shutil.copy2(src, dest)


with open("photos_bad.txt", "w", encoding='utf-8') as f:
    f.writelines([x + "\n" for x in photos_to_process_manually])
with open("photos_bad_files.txt", "w", encoding='utf-8') as f:
    f.writelines([x + "\n" for x in photos_without_file_coords])
with open("photos_adapted.txt", "w", encoding='utf-8') as f:
    f.writelines([x + "\n" for x in photos_file_coords_updated])
with open("photos_good.txt", "w", encoding='utf-8') as f:
    f.writelines([x + "\n" for x in good_photos])
print("DONE")
