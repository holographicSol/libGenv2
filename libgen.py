""" Written by Benjamin Jack Cullen

Compile using Python 3.11.

"""

import os
import sys
import re
import dataclasses
import string
import time
import shutil
import datetime
import random

import bs4
import colorama
import codecs
import asyncio
import aiohttp
import aiofiles
import aiofiles.os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dataclasses import dataclass
import ebook_ext
import libgen_help
import httprci
import get_input

# Platform check (Be compatible with Termux on Android, skip Pyqt5 import)
player_default = object
if os.name in ('nt', 'dos'):
    try:
        from PyQt5.QtCore import QUrl
        from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
        from threading import Thread

        # Initialize Notification Player_default In Memory
        player_url_default = QUrl.fromLocalFile("./resources/sound/coin_collect.mp3")
        player_content_default = QMediaContent(player_url_default)
        player_default = QMediaPlayer()
        player_default.setMedia(player_content_default)
        player_default.setVolume(6)
        mute_default_player = True
    except:
        pass

# Colorama requires initialization before use
colorama.init()

# Global mirrors
mirror_search = ''
mirror_phase_one = 'http://library.lol'


# return headers with a random user agent
def user_agent():
    ua = UserAgent()
    return {'User-Agent': str(ua.random)}


# create a dataclass for performance increase (instead of plugging everything into function arguments)
@dataclass(slots=True)
class DownloadArgs:
    verbose: bool
    url: list
    filename: str
    filepath: str
    chunk_size: int
    clear_n_chars: int
    min_file_size: int
    log: bool
    success_downloads: list
    failed_downloads: list
    ds_bytes: bool
    preferred_dl_link: str
    link_index: int


_retry_download = int(0)

# set master timeout
master_timeout = 86400  # 24h

# set scraper timeout/connection-issue retry time intervals
timeout_retry = 2
connection_error_retry = 10
server_disconnected_error_retry = 10
client_payload_error_retry = 10

# configure options for scraping
scrape_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=master_timeout,  # How long to wait before an open socket allowed to connect
    sock_read=master_timeout  # How long to wait with no data being read before timing out
)
client_args = dict(
    trust_env=True,
    timeout=scrape_timeout
)

# configure options for downloading files
download_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=master_timeout,  # How long to wait before an open socket allowed to connect
    sock_read=master_timeout  # How long to wait with no data being read before timing out
)
client_args_download = dict(
    trust_env=True,
    timeout=download_timeout
)


def color(s: str, c: str) -> str:
    """ color print """
    if c == 'W':
        return colorama.Style.BRIGHT + colorama.Fore.WHITE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LM':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'M':
        return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + str(s) + colorama.Style.RESET_ALL
    elif c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'B':
        return colorama.Style.BRIGHT + colorama.Fore.BLUE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LG':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL


def get_dt() -> str:
    """ formatted datetime string for tagging output """
    return color(str('[' + str(datetime.datetime.now()) + ']'), c='W')


def convert_bytes(num: int) -> str:
    """ bytes for humans """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def play():
    """ Notification sound """
    if os.name in ('nt', 'dos'):
        player_default.play()
        time.sleep(1)


def out_of_disk_space(_chunk_size: int) -> bool:
    """ Free disk space check """
    total, used, free = shutil.disk_usage("./")
    if free > _chunk_size + 1024:
        return False
    else:
        return True


def index_preferred_download_link(_urls: list, _preferred_dl_link: str):
    """ By default, finds and returns index number of Cloudflare download url """
    _link_index = 2
    if not _preferred_dl_link == 'none_specified':
        i_url = 0
        for url in _urls:
            if str(_preferred_dl_link).strip() in str(url).strip() and i_url >= 2:
                _link_index = i_url
                break
            i_url += 1
    return _link_index


def make_file_name(_title: str, _url: str, _filepath: str) -> str:
    """ Create safe filename using string from book URL"""

    # Use filepath safe characters
    invalid_char = '<>:"/|?*'
    new_filename = ''
    for char in _title:
        if char not in invalid_char:
            new_filename += char

    # Use only single spaces
    new_filename = new_filename.strip()
    new_filename = re.sub('\s+', ' ', new_filename)

    # Find URL suffix
    url_idx = _url.rfind('.')
    ext = _url[url_idx:]

    # Modify filename if filename is a Windows reserved filename
    win_res_nm = ['CON', 'PRN', 'AUX', 'NUL',
                  'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                  'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if new_filename in win_res_nm:
        rand_string = ''.join(random.choice(string.digits) for digi in range(32))
        new_filename += '_'+rand_string

    # Make filename length < max filename length limit
    _len_filename = len(_filepath) + len(new_filename) + len(ext)
    if _len_filename >= 255:
        new_filename = new_filename[:250-len(_filepath)-len(ext)]
        new_filename = new_filename + '...'

    # Append filename suffix to filename
    new_filename += ext

    return new_filename


async def download_file(dyn_download_args: dataclasses.dataclass) -> bool:

    """
    This function is currently designed to run synchronously while also having asynchronous features.
    Make use of faster async read/write and aiohhttp while also not needing to make this function non-blocking -
    (This function runs one instance at a time to prevent being soft/hard blocked from server(s)). """

    # Output: Link index
    print(f'{get_dt()} ' + color('[Link Index] ', c='LC') + color(str(dyn_download_args.link_index), c='W'))

    # Output: Filename and download link
    print(f'{get_dt()} ' + color('[Book] ', c='LC') + color(str(dyn_download_args.filename), c='LG'))

    _chunk_size = dyn_download_args.chunk_size
    print(f'{get_dt()} ' + color('[URL] ', c='LC') + color(str(dyn_download_args.url[dyn_download_args.link_index]), c='W'))

    # Check: Filename exists in filesystem save location
    if not os.path.exists(dyn_download_args.filename):

        # Check: Filename exists in books_saved.txt
        if dyn_download_args.filename not in success_downloads:

            try:
                async with aiohttp.ClientSession(headers=user_agent(), **client_args_download) as session:
                    async with session.get(dyn_download_args.url[dyn_download_args.link_index]) as r:
                        if dyn_download_args.verbose is True:
                            print(f'{get_dt()} ' + color('[Response] ', c='Y') + f'{httprci.get(r.status, int(3))}')
                        if r.status == 200:

                            # keep track of how many bytes have been downloaded
                            _sz = int(0)

                            # open file to write the bytes into
                            async with aiofiles.open(dyn_download_args.filepath+'.tmp', mode='wb') as handle:

                                # iterate over chunks of bytes in the response
                                async for chunk in r.content.iter_chunked(_chunk_size):

                                    # storage check:
                                    if await asyncio.to_thread(out_of_disk_space, _chunk_size=dyn_download_args.chunk_size) is False:

                                        # write chunk to the temporary file
                                        await handle.write(chunk)

                                        # output: display download progress
                                        _sz += int(len(chunk))
                                        print(' ' * dyn_download_args.clear_n_chars, end='\r', flush=True)
                                        if dyn_download_args.ds_bytes is False:
                                            print(f'[DOWNLOADING] {str(convert_bytes(_sz))}', end='\r', flush=True)
                                        else:
                                            print(f'[DOWNLOADING] {str(_sz)} bytes', end='\r', flush=True)
                                    else:
                                        # output: out of disk space
                                        print(' ' * dyn_download_args.clear_n_chars, end='\r', flush=True)
                                        print(str(color(s='[WARNING] OUT OF DISK SPACE! Download terminated.', c='Y')), end='\r', flush=True)

                                        # delete temporary file if exists
                                        if os.path.exists(dyn_download_args.filepath + '.tmp'):
                                            await handle.close()
                                            await aiofiles.os.remove(dyn_download_args.filepath + '.tmp')
                                        # exit.
                                        print('\n\n')
                                        exit(0)
                            await handle.close()

            except asyncio.exceptions.TimeoutError:
                print(f'{get_dt()} ' + color(f'[TimeoutError] Enumeration timeout. Retrying in {timeout_retry} seconds.', c='Y'))
                await asyncio.sleep(timeout_retry)
                await download_file(dyn_download_args)

            except aiohttp.ClientConnectorError:
                print(f'{get_dt()} ' + color(f'[ClientConnectorError] Enumeration connection error. Retrying in {connection_error_retry} seconds.', c='Y'))
                await asyncio.sleep(connection_error_retry)
                await download_file(dyn_download_args)

            except aiohttp.ServerDisconnectedError:
                print(f'{get_dt()} ' + color(f'[ServerDisconnectedError] Retrying in {server_disconnected_error_retry} seconds.', c='Y'))
                await asyncio.sleep(server_disconnected_error_retry)
                await download_file(dyn_download_args)

            except aiohttp.ClientPayloadError:
                print(f'{get_dt()} ' + color(f'[ClientPayloadError] Retrying in {client_payload_error_retry} seconds.', c='Y'))
                await asyncio.sleep(client_payload_error_retry)
                await download_file(dyn_download_args)

            if os.path.exists(dyn_download_args.filepath+'.tmp'):

                """
                CHECK: temporary file worth keeping? (<1024 bytes would be less than 1024 characters, reduce this if
                       needed).
                       Sometimes file exists on a different server, this software does not intentionally follow any
                       external links, if the file is in another place then a very small file may be downloaded because
                       ultimately the file we wanted was not present and will then be detected and deleted.
                  """

                if os.path.getsize(dyn_download_args.filepath+'.tmp') >= dyn_download_args.min_file_size:

                    if dyn_download_args.verbose is True:
                        print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Attempting to replace temporary file with actual file.', c='LC'))

                    # create final download file from temporary file
                    await aiofiles.os.replace(dyn_download_args.filepath+'.tmp', dyn_download_args.filepath)

                    # display download success (doesn't guarantee a usable file, checks are performed before this point)
                    if os.path.exists(dyn_download_args.filepath):

                        if dyn_download_args.verbose is True:
                            print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Replaced temporary file successfully.', c='LC'))
                        print(f'{get_dt()} ' + color('[Downloaded Successfully]', c='G'))

                        # check: clean up the temporary file if it exists.
                        if os.path.exists(dyn_download_args.filepath + '.tmp'):
                            await aiofiles.os.remove(dyn_download_args.filepath + '.tmp')
                        if dyn_download_args.verbose is True:
                            if not os.path.exists(dyn_download_args.filepath + '.tmp'):
                                print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Removed temporary file.', c='LC'))

                        # add book to saved list. multi-drive/system memory (continue where you left off)
                        if dyn_download_args.log is True:
                            if dyn_download_args.filename not in success_downloads:
                                success_downloads.append(dyn_download_args.filename)
                                async with aiofiles.open('./books_saved.txt', mode='a+', encoding='utf8') as handle:
                                    await handle.write(dyn_download_args.filename + '\n')
                                await handle.close()

                            # read file and check if new entry exists
                            if dyn_download_args.verbose is True:
                                async with aiofiles.open('./books_saved.txt', mode='r', encoding='utf8') as handle:
                                    text = await handle.read()
                                await handle.close()
                                lines = text.split('\n')
                                if dyn_download_args.filename in lines:
                                    print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Successfully added book to books_saved.txt', c='LC'))
                                else:
                                    print(f'{get_dt()} ' + color('[File] ', c='R') + color(f'Failed to add book to books_saved.txt', c='LC'))

                        return True

                    else:
                        if dyn_download_args.verbose is True:
                            print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Issue replacing temporary file.', c='LC'))

                else:
                    print(f'{get_dt()} ' + color(f'[Download Failed] ', c='R') + str(''))

                    # check: clean up the temporary file if it exists.
                    if os.path.exists(dyn_download_args.filename+'.tmp'):
                        os.remove(dyn_download_args.filename+'.tmp')

                    # check: path still exists
                    if dyn_download_args.verbose is True:
                        if not os.path.exists(dyn_download_args.filename+'.tmp'):
                            print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Successfully removed temporary file.', c='LC'))
                        else:
                            print(f'{get_dt()} ' + color('[File] ', c='R') + color(f'Failed to remove temporary file.', c='LC'))

                    return False
        else:
            print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File exists in records.', c='W'))
    else:
        print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File already exists in filesystem.', c='W'))


def get_soup(_body: str) -> bs4.BeautifulSoup:
    """ return soup """
    return BeautifulSoup(_body, 'html.parser')


def parse_soup_phase_one(_soup: bs4.BeautifulSoup) -> list:
    """ parse soup from phase one (parse for book URLs) """
    book_urls = []
    check_0 = [str(mirror_phase_one) + '/main/']
    for link in _soup.find_all('a'):
        href = link.get('href')
        if str(href).startswith(tuple(check_0)):
            book_urls.append([href])
    return book_urls


def parse_soup_phase_two(_soup: bs4.BeautifulSoup, _book_urls: list) -> list:
    """ parse soup from phase two (parse book URLs (found in phase one) for a specific tag) """
    for row in _soup.find_all('td'):
        title = list(str(row.getText('h1')).split('\n'))
        if len(title) >= 8:
            title = title[7]
            title = title[2:]
            title = title[:-2]
            # filter download title
            if title not in _book_urls:
                _book_urls.append(title)
                break

    for link in _soup.find_all('a'):
        href = link.get('href')
        # filter download links
        if str(href).endswith(tuple(ebook_ext.ebook_extensions_1)):
            if str(href) not in _book_urls:
                _book_urls.append(str(href))
    return _book_urls


async def scrape_pages(url: str) -> list:
    """ scrape for book URLs """
    book_urls = []
    try:
        _headers = user_agent()
        async with aiohttp.ClientSession(headers=_headers, **client_args) as session:
            async with session.get(url) as r:
                _body = await r.text(encoding=None, errors='ignore')
                _soup = await asyncio.to_thread(get_soup, _body=_body)
                book_urls = await asyncio.to_thread(parse_soup_phase_one, _soup=_soup)

    except asyncio.exceptions.TimeoutError:
        print(f'{get_dt()} ' + color(f'[TimeoutError] Initial scraper timeout. Retrying in {timeout_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await scrape_pages(url)

    except aiohttp.ClientConnectorError:
        print(f'{get_dt()} ' + color(f'[ClientConnectorError] Initial scraper connection error. Retrying in {connection_error_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await scrape_pages(url)

    except aiohttp.ServerDisconnectedError:
        print(f'{get_dt()} ' + color(f'[ServerDisconnectedError] Retrying in {server_disconnected_error_retry} seconds.', c='Y'))
        await asyncio.sleep(server_disconnected_error_retry)
        await scrape_pages(url)

    except aiohttp.ClientPayloadError:
        print(f'{get_dt()} ' + color(f'[ClientPayloadError] Retrying in {client_payload_error_retry} seconds.', c='Y'))
        await asyncio.sleep(client_payload_error_retry)
        await scrape_pages(url)

    return book_urls


async def enumerate_links(_book_urls: list, _verbose: bool) -> list:
    """ scrape for book download links """

    try:
        _headers = user_agent()
        async with aiohttp.ClientSession(headers=_headers, **client_args) as session:
            async with session.get(_book_urls[0]) as r:
                # print(r.status)
                if r.status == 200:
                    _body = await r.text(encoding=None, errors='ignore')
                    _soup = await asyncio.to_thread(get_soup, _body=_body)
                    if _soup:
                        data = await asyncio.to_thread(parse_soup_phase_two, _soup=_soup, _book_urls=_book_urls)
                        # base urls, title, download links
                        if len(data) >= 3:
                            # when all the lights turn green we have everything we need
                            if _verbose is True:
                                print(f'{get_dt()} ' + color(f'[RESPONSE] {str(r.status)}. {_book_urls}', c='G'))
                            return data
                else:
                    # retry because the response was not 200
                    if _verbose is True:
                        print(f'{get_dt()} ' + color(f'[RESPONSE] {str(r.status)}. Retrying: {_book_urls}', c='Y'))
                    await asyncio.sleep(2)
                    await enumerate_links(_book_urls=_book_urls, _verbose=_verbose)

    except asyncio.exceptions.TimeoutError:
        if _verbose is True:
            print(f'{get_dt()} ' + color(f'[TimeoutError] Enumeration timeout. Retrying in {timeout_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await enumerate_links(_book_urls=_book_urls, _verbose=_verbose)

    except aiohttp.ClientConnectorError:
        if _verbose is True:
            print(f'{get_dt()} ' + color(f'[ClientConnectorError] Enumeration connection error. Retrying in {connection_error_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await enumerate_links(_book_urls=_book_urls, _verbose=_verbose)

    except aiohttp.ServerDisconnectedError:
        if _verbose is True:
            print(f'{get_dt()} ' + color(f'[SERVER DISCONNECTED] Retrying in {server_disconnected_error_retry} seconds.', c='Y'))
        await asyncio.sleep(server_disconnected_error_retry)
        await enumerate_links(_book_urls=_book_urls, _verbose=_verbose)

    except aiohttp.ClientPayloadError:
        print(f'{get_dt()} ' + color(f'[ClientPayloadError] Retrying in {client_payload_error_retry} seconds.', c='Y'))
        await asyncio.sleep(client_payload_error_retry)
        await enumerate_links(_book_urls=_book_urls, _verbose=_verbose)

    if len(_book_urls) >= 3:
        # base urls, title, download links
        return _book_urls


async def run_downloader(dyn_download_args):
    global _retry_download

    # download file
    dl_tasks = []
    dl_task = asyncio.create_task(download_file(dyn_download_args))
    dl_tasks.append(dl_task)
    dl = await asyncio.gather(*dl_tasks)

    if dl[0] is True:

        # Notification sound after platform check
        if os.name in ('nt', 'dos'):
            if mute_default_player is False:
                play_thread = Thread(target=play)
                play_thread.start()


async def main(_i_page=1, _max_page=88, _exact_match=False, _search_q='', _lib_path='./library/',
               _success_downloads=None, _failed_downloads=None, _ds_bytes=False, _verbose=False,
               _results_per_page='50', _column='title', _preferred_dl_link=''):

    global _retry_download

    # Phase One: Setup async scaper to get book URLs (one page at a time to prevent getting kicked from the server)
    if _success_downloads is None:
        _success_downloads = []
    for i_current_page in range(i_page, _max_page):

        # create URL to scrape using query and exact match bool
        url = str(str(mirror_search) + '/search.php?req=' + str(_search_q).replace(' ', '+'))
        url = url + f'&open=0&res={str(_results_per_page)}&view=simple&phrase=1&column={_column}&page='
        url = url+str(i_current_page)

        print(f'{get_dt()} ' + color('[Search] ', c='LC') + color(search_q, c='W'))
        print(f'{get_dt()} ' + color('[Page] ', c='LC') + f'Page: {i_current_page}')
        print(f'{get_dt()} ' + color('[Scanning] ', c='LC') + f'{url}')
        print(f'{get_dt()} ' + color('[Phase One] ', c='LC') + f'Gathering initial links...')

        tasks = []
        t0 = time.perf_counter()
        task = asyncio.create_task(scrape_pages(url))
        tasks.append(task)
        results = await asyncio.gather(*tasks)
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Results] ', c='Y') + color(str(results), c='LC'))
        for result in results:
            if result is None:
                del result
        results[:] = [item for sublist in results for item in sublist if item is not None]
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Results Formatted] ', c='Y') + color(str(results), c='LC'))

        # Displays Zero if none found
        print(f'{get_dt()} ' + color('[Results] ', c='Y') + f'{len(results)}')
        print(f'{get_dt()} ' + color('[Phase One Time] ', c='LC') + f'{time.perf_counter()-t0}')

        if len(results) == int(0):
            print(f'{get_dt()} ' + color('[Max Page] ', c='LC') + f'No results were found on page {i_current_page}. Exiting.')
            print('\n\n')
            break

        # Phase Two: Setup async scaper to get book download links for each book on the current page
        print(f'{get_dt()} ' + color('[Phase Two] ', c='LC') + f'Enumerating Links...')
        t0 = time.perf_counter()
        tasks = []
        for result in results:
            task = asyncio.create_task(enumerate_links(_book_urls=result, _verbose=_verbose))
            tasks.append(task)
        enumerated_results = await asyncio.gather(*tasks)
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Enumerated Results] ', c='Y') + color(str(enumerated_results), c='LC'))
        print(f'{get_dt()} ' + color('[Enumerated Results] ', c='LC') + f'{len(enumerated_results)}')
        enumerated_results[:] = [item for item in enumerated_results if item is not None]

        if _verbose is True:
            print(f'{get_dt()} ' + color('[Enumerated Results Formatted] ', c='Y') + color(str(enumerated_results), c='LC'))
        print(f'{get_dt()} ' + color('[Enumerated Results Formatted] ', c='LC') + f'{len(enumerated_results)}')
        print(f'{get_dt()} ' + color('[Phase Two Time] ', c='LC') + f'{time.perf_counter()-t0}')

        # uncomment to see all
        # for enumerated_result in enumerated_results:
        #     print(enumerated_result)
        # break

        # uncomment to see what may have been missed
        # for enumerated_result in enumerated_results:
        #     if len(enumerated_result) < 3:
        #         print(enumerated_result)
        # break

        # Current book on current page
        i_current_book = 0

        # Synchronously (for now) attempt to download each book on the current page.
        for enumerated_result in enumerated_results:

            if len(enumerated_result) >= 3:
                print('_' * 28)
                print('')
                print(f'{get_dt()} {color("[Progress] ", c="LC")} {color(str(f"{i_current_book+1}/{len(enumerated_results)} ({i_current_page}/{_max_page})"), c="W")}')
                print(f'{get_dt()} ' + color('[Category] ', c='LC') + color(str(_search_q), c='W'))
                if _verbose is True:
                    print(f'{get_dt()} ' + color('[Handling Enumerated Result] ', c='Y') + color(str(enumerated_result), c='LC'))

                # Check: Library category directory exists
                if not os.path.exists(lib_path + '/' + _search_q):
                    os.makedirs(lib_path + '/' + _search_q, exist_ok=True)

                # Make filename from URL and title:

                # Default 2: [0] Base URL, [1] Title, [2+] Download links.
                _link_index = index_preferred_download_link(_urls=enumerated_result,
                                                            _preferred_dl_link=_preferred_dl_link)

                filepath = lib_path + '/' + _search_q + '/'

                # Create filename using filepath and url[_link_index] extension
                filename = make_file_name(_title=enumerated_result[1],
                                          _url=enumerated_result[_link_index],
                                          _filepath=filepath)

                filepath = filepath + filename

                # create a dataclass for the downloader then run the downloader handler
                dyn_download_args = DownloadArgs(verbose=_verbose,
                                                 url=enumerated_result,
                                                 filename=filename,
                                                 filepath=filepath,
                                                 chunk_size=8192,
                                                 clear_n_chars=50,
                                                 min_file_size=1024,
                                                 log=True,
                                                 success_downloads=_success_downloads,
                                                 failed_downloads=_failed_downloads,
                                                 ds_bytes=_ds_bytes,
                                                 preferred_dl_link=_preferred_dl_link,
                                                 link_index=_link_index)
                _retry_download = 0
                await run_downloader(dyn_download_args)

            i_current_book += 1

        libgen_help.display_banner()

# Get STDIN and parse
stdin = list(sys.argv)

if '-h' in stdin:
    libgen_help.display_help()

elif '-h' not in stdin and len(stdin) >= 2:
    libgen_help.display_banner()

    verbose = get_input.get_verbose(stdin)

    mute_default_player = get_input.get_mute(stdin)

    lib_path = get_input.get_lib_path(stdin)

    exact_match = False

    i_page = get_input.get_page(stdin)

    results_per_page = get_input.get_rmax(stdin)

    search_q = get_input.get_query(stdin)

    max_page = get_input.get_max_page(stdin)

    ds_bytes = get_input.get_display_bytes(stdin)

    column = get_input.get_column(stdin)

    preferred_dl_link = get_input.get_preferred_dl(stdin)

    mirror_search = get_input.get_search_mirror(stdin)

    mirror_phase_one = get_input.get_phase_one_mirror(stdin)

    success_downloads, failed_downloads = get_input.get_mem(stdin)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(_i_page=i_page, _max_page=max_page, _exact_match=exact_match, _search_q=search_q,
                                 _lib_path=lib_path, _success_downloads=success_downloads,
                                 _failed_downloads=failed_downloads, _ds_bytes=ds_bytes, _verbose=verbose,
                                 _results_per_page=results_per_page,
                                 _column=column, _preferred_dl_link=preferred_dl_link))

else:
    libgen_help.display_help()
