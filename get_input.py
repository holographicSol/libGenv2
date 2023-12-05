import os
import codecs


def get_verbose(stdin):
    verbose = False
    if '-v' in stdin:
        verbose = True
    return verbose


def get_mute(stdin):
    mute_default_player = True
    if os.name in ('nt', 'dos'):
        if '-sfx' in stdin:
            mute_default_player = False
    return mute_default_player


def get_lib_path(stdin):
    """ Download location """
    lib_path = './library/'
    if '-P' in stdin:
        idx = stdin.index('-P') + 1
        lib_path = stdin[idx]
    return lib_path


def get_page(stdin):
    """ Start downloads from this page """
    i_page = 1
    if '-p' in stdin:
        idx = stdin.index('-p') + 1
        i_page = int(stdin[idx])
    return i_page


def get_max_page(stdin):
    """ Stop downloading on this page """
    max_page = 100
    if '-max' in stdin:
        idx = stdin.index('-max') + 1
        max_page = int(stdin[idx])
    return max_page


def get_rmax(stdin):
    """ Maximum number of results per page """
    results_per_page = '50'
    allowed_results_per_page = ['25', '50', '100']
    if '-rmax' in stdin:
        idx = stdin.index('-rmax') + 1
        input_results_per_page = stdin[idx]
        if input_results_per_page in allowed_results_per_page:
            results_per_page = input_results_per_page
    return results_per_page


def get_query(stdin):
    """ Books containing query will be downloaded"""
    search_q = ''
    if '-k' in stdin:
        idx = stdin.index('-k')+1
        i = 0
        for x in stdin:
            if i >= int(idx):
                search_q = search_q + ' ' + x
            i += 1
        search_q = search_q[1:]
    return search_q


def get_display_bytes(stdin):
    """ Show download progress in bytes """
    ds_bytes = False
    if '-bytes' in stdin:
        ds_bytes = True
    return ds_bytes


def get_column(stdin):
    """ Title vs Author Search """
    column = 'title'
    if '--author' in stdin:
        column = 'author'
    return column


def get_preferred_dl(stdin):
    """ Be polite. Use cloudflare """
    preferred_dl_link = 'none_specified'
    if '--cloudflare' in stdin:
        preferred_dl_link = 'https://cloudflare'
    return preferred_dl_link


def get_search_mirror(stdin):
    """ Mirror used when crawling for results """
    mirror_search = 'https://libgen.is'
    if '--search-mirror' in stdin:
        idx = stdin.index('--search-mirror') + 1
        mirror_search = stdin[idx]
    return mirror_search


def get_phase_one_mirror(stdin):
    """ Mirror used when obtaining book webpage URLs from initial results """
    mirror_phase_one = 'http://library.lol'
    if '--phase-one-mirror' in stdin:
        idx = stdin.index('--phase-one-mirror') + 1
        mirror_phase_one = stdin[idx]
    return mirror_phase_one


def get_mem(stdin):
    """ Run with amnesia. Ignore logs and download anyway. """
    success_downloads = []
    failed_downloads = []

    if '--no-mem' not in stdin:

        # saved downloads
        if not os.path.exists('./books_saved.txt'):
            open('./books_saved.txt', 'w').close()
        with codecs.open('./books_saved.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line not in success_downloads:
                    success_downloads.append(line)

        # failed downloads
        if not os.path.exists('./books_failed.txt'):
            open('./books_failed.txt', 'w').close()
        with codecs.open('./books_failed.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line not in failed_downloads:
                    failed_downloads.append(line)
        fo.close()

    return success_downloads, failed_downloads


