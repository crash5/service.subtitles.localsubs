import sys
import os
from urllib.parse import urlencode, unquote_plus, parse_qsl
from pathlib import Path
from collections import namedtuple

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcplugin
import xbmcgui


__addon__ = xbmcaddon.Addon()
__scriptid__ = __addon__.getAddonInfo('id')
__profile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__temp__ = xbmcvfs.translatePath(os.path.join(__profile__, 'temp', ''))

__addon_handle__ = int(sys.argv[1])


Subtitle = namedtuple('Subtitle', ['file_name', 'location', 'language'])


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
    debuglog(f'Clean title by parent dir: {xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)}')
    debuglog(f'Clean title: {xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile())}')


##### Operations
def use_subtitle(location):
    listitem = xbmcgui.ListItem(label=location)
    add_directory_item(listitem, location)


def search():
    file_path = os.path.dirname(xbmc.Player().getPlayingFile())
    full_path = Path(xbmc.Player().getPlayingFile())
    file_no_ext = full_path.with_suffix('').name

    # file_name = xbmc.getInfoLabel("VideoPlayer.Title")
    # file_name = xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile(), True)

    dirs = [
        xbmcvfs.translatePath('special://subtitles'),
        os.path.join(file_path, 'Subs', file_no_ext),
    ]

    subtitles = []
    for dir in dirs:
        subtitles.extend(collect_subs_from_directory(dir))
    sorted_subtitles = sorted(subtitles, key=get_subtitle_weight, reverse=True)
    add_subtitles_to_ui(sorted_subtitles)
#####


def collect_subs_from_directory(subtitle_dir):
    files = get_files_from_directory(subtitle_dir)
    subtitle_files = filter(is_subtitle, files)

    subtitles = []
    for file_name in subtitle_files:
        location = os.path.join(subtitle_dir, file_name)
        # TODO: determine language if possible
        language = 'English'
        subtitles.append(Subtitle(file_name, location, language))

    return subtitles


def get_files_from_directory(directory):
    (_, files) = xbmcvfs.listdir(directory)
    return files


def is_subtitle(file):
    return file.endswith('.srt')


def get_subtitle_weight(subtitle):
    file_name = xbmc.getCleanMovieTitle(xbmc.Player().getPlayingFile())[0]
    # TODO: add additional weight to local subtitle
    return longes_common_subsequence(file_name, subtitle.file_name)[0]


# source: https://stackoverflow.com/q/67155579
def longes_common_subsequence(s1, s2):
    matrix = [[[] for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j] = [s1[i]]
                else:
                    matrix[i][j] = matrix[i - 1][j - 1] + [s1[i]]
            else:
                matrix[i][j] = max(matrix[i - 1][j], matrix[i][j - 1], key=len)
    cs = matrix[-1][-1]
    return len(cs), ''.join(cs)


def add_subtitles_to_ui(subtitles):
    for subtitle in subtitles:
        add_subtitle_to_ui(subtitle)


def add_subtitle_to_ui(subtitle):
    listitem = xbmcgui.ListItem(label=subtitle.language, label2=subtitle.file_name)
    listitem.setArt(
        {'thumb': xbmc.convertLanguage(subtitle.language, xbmc.ISO_639_1)}
    )
    url = create_use_subtitle_url(subtitle.location)
    add_directory_item(listitem, url)


def create_use_subtitle_url(location):
    params = {
        'action': 'use',
        'location': location
    }
    return create_plugin_url(params)


def create_plugin_url(params):
    return f'plugin://{__scriptid__}/?{urlencode(params)}'


def add_directory_item(listitem, url):
    xbmcplugin.addDirectoryItem(handle=__addon_handle__, url=url, listitem=listitem)


def parse_arguments(args):
    # action=search&languages=English&preferredlanguage=English
    return dict(parse_qsl(args))


if __name__ == '__main__':
    loginfos()

    params = parse_arguments(sys.argv[2][1:])

    if params['action'] == 'search':
        search()
    elif params['action'] == 'use':
        location = unquote_plus(params['location'])
        use_subtitle(location)
    else:
        exit('Unknown action')

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
