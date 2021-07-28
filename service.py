import sys
import os

import xbmc
import xbmcaddon
import xbmcvfs

import xbmcplugin
import xbmcgui

from urllib.parse import urlencode, unquote_plus, parse_qsl

from pathlib import Path


__addon__ = xbmcaddon.Addon()
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

__cwd__ = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
__profile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__temp__ = xbmcvfs.translatePath(os.path.join(__profile__, 'temp', ''))

__addon_handle__ = int(sys.argv[1])


def debuglog(msg):
    xbmc.log(u"### [%s] - %s" % (__scriptid__, msg), level=xbmc.LOGINFO)


def loginfos():
    debuglog(f'args: {sys.argv}')
    debuglog(f'VideoPlayer.OriginalTitle: {xbmc.getInfoLabel("VideoPlayer.OriginalTitle")}')
    debuglog(f'VideoPlayer.Title: {xbmc.getInfoLabel("VideoPlayer.Title")}')
    debuglog(f'Playing file: {xbmc.Player().getPlayingFile()}')

    debuglog(f'VideoPlayer.TVshowtitle: {xbmc.getInfoLabel("VideoPlayer.TVshowtitle")}')
    debuglog(f'VideoPlayer.Season: {xbmc.getInfoLabel("VideoPlayer.Season")}')
    debuglog(f'VideoPlayer.Episode: {xbmc.getInfoLabel("VideoPlayer.Episode")}')
    debuglog(f'Clean title: {xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)}')


def add_sub_from_dir(subtitle_dir):
    file_name = xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)

    (_, files) = xbmcvfs.listdir(subtitle_dir)

    sorted_names = sorted(
        files,
        key=lambda x: longes_common_subsequence(file_name[0], x)[0],
        reverse=True)

    for file in sorted_names:
        location = os.path.join(subtitle_dir, file)

        params = {
            'action': 'use',
            'location': location}

        add_directory_item(
            create_sub_listitem(file),
            create_plugin_url(params)
        )


def search():
    file_path = os.path.dirname(xbmc.Player().getPlayingFile())

    full_path = Path(xbmc.Player().getPlayingFile())
    file_no_ext = full_path.with_suffix('').name

    # file_name = xbmc.getInfoLabel("VideoPlayer.Title")
    # file_name = xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)


    # kodi_subtitle_dir = xbmcvfs.translatePath('special://subtitles')
    # if xbmcvfs.exists(kodi_subtitle_dir):
    #     add_sub_from_dir(kodi_subtitle_dir)

    under_subs_dir = os.path.join(file_path, 'Subs', file_no_ext) 
    if xbmcvfs.exists(under_subs_dir + '/'):
        add_sub_from_dir(under_subs_dir)


# def cleanup_temp():
#     location = __temp__
#     if xbmcvfs.exists(location):
#         (dirs, files) = xbmcvfs.listdir(location)
#         for file in files:
#             xbmcvfs.delete(os.path.join(location, file))
#         for dir in dirs:
#             xbmcvfs.rmdir(os.path.join(location, dir), force=True)
#     else:
#         xbmcvfs.mkdirs(location)


def create_plugin_url(params):
    return f'plugin://{__scriptid__}/?{urlencode(params)}'


def add_directory_item(listitem, url):
    xbmcplugin.addDirectoryItem(handle=__addon_handle__, url=url, listitem=listitem)


def create_sub_listitem(file_name):
    listitem = xbmcgui.ListItem(label='English', label2=file_name)
    listitem.setArt(
        {'thumb': xbmc.convertLanguage('en', xbmc.ISO_639_1)}
    )
    return listitem


def use_subtitle(location):
    listitem = xbmcgui.ListItem(label=location)
    add_directory_item(listitem, location)


def download(url):
    # cleanup_temp()
    # download
    use_subtitle(url)


def longes_common_subsequence(s1, s2):
    matrix = [["" for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j] = s1[i]
                else:
                    matrix[i][j] = matrix[i-1][j-1] + s1[i]
            else:
                matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1], key=len)

    cs = matrix[-1][-1]

    return len(cs), cs


def parse_arguments(args):
    # action=search&languages=English&preferredlanguage=English
    return dict(parse_qsl(args))


if __name__ == '__main__':
    loginfos()

    params = parse_arguments(sys.argv[2][1:])

    if params['action'] == 'search':
        search()
    elif params['action'] == 'download':
        url = unquote_plus(params['url'])
        download(url)
    elif params['action'] == 'use':
        location = unquote_plus(params['location'])
        use_subtitle(location)
    else:
        exit('Unknow action')

    xbmcplugin.endOfDirectory(__addon_handle__)

# class logger:
#     @staticmethod
#     def log(message, level=xbmc.LOGDEBUG):
#         xbmc.log(f'{__scriptid__}: {message}', level)

#     @staticmethod
#     def info(message):
#         logger.log(message, xbmc.LOGINFO)

#     @staticmethod
#     def error(message):
#         logger.log(message, xbmc.LOGERROR)

#     @staticmethod
#     def debug(message):
#         logger.log(message, xbmc.LOGDEBUG)

