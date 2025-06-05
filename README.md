
[  LibGenesis Downloader   ]

    -k                   Keyword            Specify a search string.
    -p                   Page               Specify a page to start downloading from (optional). (Default -p 1)
    -P                   Path               Specify save path (optional). (Default -P ./library)
    -max                 Max                Specify a page to end downloading (optional). -max 3. (Default -max 100)
    -rmax                RMax               Specify max results per page. (25, 50, 100). (Default -rmax 50).
    --title              Title Search       Search for titles containing -k. (Default).
    --author             Author Search      Search for author -k.
    --cloudflare         Use Cloudflare     Be Polite. Use cloudflare download links when available.
    --search-mirror      Search Mirror      Set initial search mirror. (Default: https://libgen.is)
    --phase-one-mirror   Phase One Mirror   Set phase one mirror. (Default: http://library.lol)
    --cloudflare         Use Cloudflare     Be Polite. Use cloudflare download links when available.
    --no-mem             No Memory          Do not use books_saved.txt when ascertaining if file will be downloaded.
    -v                   Verbosity          Increase verbosity.
    -h                   Help               Displays this help message.

Developed and written by Benjamin Jack Cullen.

Key Errors may be a result of libgen mirror max user reached, in this case try using cloudflare argument (recommended anyway).

Example Useage: libgen -v --cloudflare -P D:\Books\ --title -k natural sciences

Updated: 19/5/2025
Requires Update: 04/06/2025

Windows Executable:
Download: https://drive.google.com/drive/folders/1PdejPEIesD3Y6zVapXLfE-h76X310Pkl?usp=sharing
