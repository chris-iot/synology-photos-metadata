import requests
from .photo import Photo


# album class
class Album(object):
    def __init__(self, id, sharepath, name, title):
        self.id = id
        self.sharepath = sharepath
        self.name = name
        self.title = title

    def __str__(self):
        return f"{self.name} ({self.title}): path='{self.sharepath}' <{self.id}>"

    @classmethod
    def albums(cls, base_url, root_id=None):
        album_url = base_url + 'album.php?api=SYNO.PhotoStation.Album&version=1&method=list&limit=10000&offset=0&type=album'
        if root_id is not None:
            album_url += '&id=' + str(root_id)
        try:
            for item in requests.get(album_url).json()['data']['items']:
                yield Album(id=item['id'],
                            sharepath=item['info']['sharepath'],
                            name=item['info']['name'],
                            title=item['info']['title'])
                yield from Album.albums(base_url, root_id=item['id'])
        except:  # most likely we end up here e.g. in case of password protected albums...
            pass

    def photos(self, base_url, album_id=None):
        photos_url = base_url + 'photo.php?api=SYNO.PhotoStation.Photo&version=1&method=list&limit=100000' + \
                     '&offset=0&type=photo&additional=photo_exif'
        if album_id is not None:
            photos_url += '&filter_album=' + str(album_id)
        else:
            photos_url += '&filter_album=' + str(self.id)
        try:
            for item in requests.get(photos_url).json()['data']['items']:
                yield Photo(id=item['id'],
                            name=item['info']['name'],
                            title=item['info']['title'],
                            latitude=item['info']['lat'],
                            longitude=item['info']['lng'],
                            gps_lat=item['additional']['photo_exif']['gps']['lat'] if item['additional']['photo_exif']['gps'] is not None else None,
                            gps_lng=item['additional']['photo_exif']['gps']['lng'] if item['additional']['photo_exif']['gps'] is not None else None)
        except:  # most likely we end up here e.g. in case of password protected albums...
            pass
