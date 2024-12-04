import cloudscraper

from .common import InfoExtractor


class ThisAVIE(InfoExtractor):
    _VALID_URL = (
        r'https?://(?:www\.)?(?:thisav|missav)\.com(?:/([^/]+))*/(?P<id>.*)'
    )
    _TESTS = [
        {
            'url': 'https://thisav.com/dm13/omsk-074',
            'info_dict': {
                'id': '47omsk-074734',
                'ext': 'mp4',
                'title': 'OMSK-074 桃岡',
            },
        },
        {
            # html5 media
            'url': 'https://www.thisav.com/video/242352/nerdy-18yo-big-ass-tattoos-and-glasses.html',
            'info_dict': {
                'id': '242352',
                'ext': 'mp4',
                'title': 'Nerdy 18yo Big Ass Tattoos and Glasses',
            },
        },
    ]

    def _real_extract(self, url):
        mobj = self._match_valid_url(url)
        video_id = mobj.group('id')

        scraper = cloudscraper.create_scraper()
        webpage = scraper.get(url).text
        title = self._html_extract_title(webpage)
        video_info = self._html_search_regex(
            r'm3u8(.*?)source', webpage, 'video info', default=None,
        )
        if video_info:
            video_infos = video_info.split('|')
            base_url = (
                video_infos[8]
                + '://'
                + video_infos[7]
                + '.'
                + video_infos[6]
                + '/'
                + video_infos[5]
                + '-'
                + video_infos[4]
                + '-'
                + video_infos[3]
                + '-'
                + video_infos[2]
                + '-'
                + video_infos[1]
                + '/'
            )
            playlist_url = base_url + 'playlist.m3u8'

            playlist = scraper.get(
                playlist_url,
            ).text

            formats = []
            lines = playlist.strip().split('\n')
            for i in range(len(lines)):
                line = lines[i]
                if line.startswith('#EXT-X-STREAM-INF:'):
                    format_item = {}
                    video_url = base_url + lines[i + 1]
                    resolution = line.split(',')[-1].split('=')[-1].split('x')
                    format_item['format_id'] = str(i)
                    format_item['width'] = int(resolution[0])
                    format_item['height'] = int(resolution[1])
                    format_item['url'] = video_url
                    format_item['manifest_url'] = playlist_url
                    format_item['ext'] = 'mp4'
                    format_item['protocol'] = 'm3u8_native'
                    formats.append(format_item)
        else:
            video_info = self._html_search_regex(
                rf'{video_id}(.*?)source', webpage, 'video info', default=None,
            )
            if video_info:
                video_infos = video_info.split('|')
                video_url = (
                    video_infos[4]
                    + '://'
                    + video_infos[3]
                    + '.'
                    + video_infos[2]
                    + f'/{video_id}/{video_id}.mp4'
                )
                formats = [{'url': video_url, 'ext': 'mp4', 'format_id': 'mp4'}]

        return {'id': video_id, 'title': title, 'ext': 'mp4', 'formats': formats}
