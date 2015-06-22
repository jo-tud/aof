import pyqrcode
import os
import logging
from pyramid.path import AssetResolver
from urllib.parse import urlparse
from hashlib import md5

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)


class AOFPool():
    def __init__(self):
        pass

    def get_QRCode(self,url,size=4):
        """
        Generates an QR-Code-SVG into the directory "static/img/qrcodes"
        Filename of the SVG is an md5-hash of the uri.
        :return: relative URL or None if the url is not valid
        """

        valid_url=urlparse(url)
        if bool(valid_url.scheme):
            hash=md5()
            hash.update(url.encode('utf-8'))
            target=AssetResolver().resolve(os.path.join('aof:tmp','qrcodes',str(hash.hexdigest())+".svg")).abspath()
            if not os.path.exists(target):
                qrcode = pyqrcode.create(url)
                qrcode.svg(target,size)
            target=target.replace(AssetResolver().resolve('aof:').abspath(),"")
            target=target.replace('\\',"/")
            qrcode=target
        else:
            log.error("QRCode for {} could not be created. Seems to be an invalid URL!".format(url))
            qrcode = None
        return qrcode