import sys
import os

import xbmc
import xbmcaddon
import xbmcvfs

import xbmcplugin
import xbmcgui

from urllib.parse import urlencode, unquote_plus


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

def get_params(string=""):
    param = []
    if string == "":
        paramstring = sys.argv[2]
    else:
        paramstring = string
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def loginfos():
    debuglog(params)
    debuglog(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))
    debuglog(xbmc.getInfoLabel("VideoPlayer.Title"))
    debuglog(xbmc.Player().getPlayingFile())

    debuglog(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))
    debuglog(xbmc.getInfoLabel("VideoPlayer.Season"))
    debuglog(xbmc.getInfoLabel("VideoPlayer.Episode"))
    debuglog(xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True))


def search():
    # file_path = os.path.dirname(xbmc.Player().getPlayingFile())
    # file_name = xbmc.getInfoLabel("VideoPlayer.Title")
    file_name = xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)
    # upper_sub_dir = os.path.dirname(file_path) + '/subs'
    upper_sub_dir = '/storage/subs'
    (dirs, files) = xbmcvfs.listdir(upper_sub_dir)
    # debuglog(dirs)
    # debuglog(files)

    sorted_names = sorted(
        files,
        key=lambda x: longes_common_subsequence(file_name[0], x)[0])


    for file in reversed(sorted_names):
        location = os.path.join(upper_sub_dir, file)

        # qparams = urlencode({
        #     'action': 'download',
        #     'url': dl_url})
        # url = f'plugin://{__scriptid__}/?{qparams}'

        listitem = xbmcgui.ListItem(
            label='English',
            label2=file)
        xbmcplugin.addDirectoryItem(
            handle=__addon_handle__,
            url=location,
            listitem=listitem)


def cleanup_temp():
    if xbmcvfs.exists(__temp__):
        (dirs, files) = xbmcvfs.listdir(__temp__)
        for file in files:
            xbmcvfs.delete(path.join(__temp__, file))
        for dir in dirs:
            xbmcvfs.rmdir(path.join(__temp__, dir), force=True)
    else:
        xbmcvfs.mkdirs(__temp__)


def download(url):
    debuglog('download')
    # loginfos()
    cleanup_temp()

    destination_file = os.path.join(__temp__, 'sadtest.srt') 

    xbmcvfs.copy(url, destination_file)

    listitem = xbmcgui.ListItem('letoltott')
    xbmcplugin.addDirectoryItem(
        handle=__addon_handle__,
        url=destination_file,
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
    params = get_params()
    # debuglog(sys.argv)
    # loginfos()

    if params['action'] == 'search':
        search()
    elif params['action'] == 'download':
        url = unquote_plus(params['url'])
        debuglog(url)
        download(url)

    # ?action=search&languages=English&preferredlanguage=English
    xbmcplugin.endOfDirectory(__addon_handle__)
