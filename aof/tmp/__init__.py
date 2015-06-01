__author__ = 'khoerfurter'

import logging
log = logging.getLogger(__name__)

def clear_all_tmp_files():
    import os
    from pyramid.path import AssetResolver

    for root, dirs, files in os.walk(AssetResolver().resolve('aof:tmp').abspath()):
        for file in files:
            if file!="__init__.py" and file.find(".pyc") == -1:
                os.remove(os.path.join(root,file))

    log.info("tmp-directory cleared!")
