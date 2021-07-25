import sys
import os

import xbmc
import xbmcaddon
import xbmcvfs

import xbmcplugin
import xbmcgui

from urllib.parse import urlencode, unquote_plus, parse_qsl


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
    debuglog(f'params: {dict(parse_qsl(sys.argv[2][1:]))}')
    debuglog(f'VideoPlayer.OriginalTitle: {xbmc.getInfoLabel("VideoPlayer.OriginalTitle")}')
    debuglog(f'VideoPlayer.Title: {xbmc.getInfoLabel("VideoPlayer.Title")}')
    debuglog(f'Playing file: {xbmc.Player().getPlayingFile()}')

    debuglog(f'VideoPlayer.TVshowtitle: {xbmc.getInfoLabel("VideoPlayer.TVshowtitle")}')
    debuglog(f'VideoPlayer.Season: {xbmc.getInfoLabel("VideoPlayer.Season")}')
    debuglog(f'VideoPlayer.Episode: {xbmc.getInfoLabel("VideoPlayer.Episode")}')
    debuglog(f'Clean title: {xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)}')


def search():
    # file_path = os.path.dirname(xbmc.Player().getPlayingFile())
    # file_name = xbmc.getInfoLabel("VideoPlayer.Title")
    file_name = xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)
    # upper_sub_dir = os.path.dirname(file_path) + '/subs'
    upper_sub_dir = '/storage/subs'
    (dirs, files) = xbmcvfs.listdir(upper_sub_dir)

    sorted_names = sorted(
        files,
        key=lambda x: longes_common_subsequence(file_name[0], x)[0])


    for file in reversed(sorted_names):
        location = os.path.join(upper_sub_dir, file)

        qparams = urlencode({
            'action': 'download',
            'url': location})
        url = f'plugin://{__scriptid__}/?{qparams}'

        listitem = xbmcgui.ListItem(
            label='English',
            label2=file)
        # list_item.setArt(
        #     {'thumb': xbmc.convertLanguage(item.language, xbmc.ISO_639_1)}
        # )
        xbmcplugin.addDirectoryItem(
            handle=__addon_handle__,
            url=url,
            listitem=listitem)


def cleanup_temp():
    if xbmcvfs.exists(__temp__):
        (dirs, files) = xbmcvfs.listdir(__temp__)
        for file in files:
            xbmcvfs.delete(os.path.join(__temp__, file))
        for dir in dirs:
            xbmcvfs.rmdir(os.path.join(__temp__, dir), force=True)
    else:
        xbmcvfs.mkdirs(__temp__)


def download(url):
    # debuglog('download')
    # loginfos()
    cleanup_temp()

    listitem = xbmcgui.ListItem(label=url)
    xbmcplugin.addDirectoryItem(
        handle=__addon_handle__,
        url=url,
        listitem=listitem)


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


if __name__ == '__main__':
    params = dict(parse_qsl(sys.argv[2][1:]))
    loginfos()

    if params['action'] == 'search':
        search()
    elif params['action'] == 'download':
        url = unquote_plus(params['url'])
        download(url)

    # ?action=search&languages=English&preferredlanguage=English
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

