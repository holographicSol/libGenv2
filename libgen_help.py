
def display_help():
    print('')
    print('')
    print('[  LibGenesis Downloader   ]')
    print('')
    print('-k         Keyword         Specify a search string.')
    print('-p         Page            Specify a page to start downloading from (optional). (Default -p 1)')
    print('-P         Path            Specify save path (optional). (Default -P ./library)')
    print('-max       Max             Specify a page to end downloading (optional). -max 3. (Default -max 100)')
    print('-rmax      RMax            Specify max results per page. (25, 50, 100). (Default -rmax 50).')
    print('--title    Title Search    Search for titles containing -k. (Default).')
    print('--author   Author Search   Search for author -k.')
    print('--no-mem   No Memory       Do not use books_saved.txt when ascertaining if file will be downloaded.')
    print('-v         Verbosity       Increase verbosity.')
    print('-h         Help            Displays this help message.')
    print('')
    print('Developed and written by Benjamin Jack Cullen.')
    print('')
    print('')
