# Async-DeviantArt-Image-Scraper
Script takes DeviantArt username and scrapes artist's images asynchronously

Setup:
* clone the repository

* cd to the cloned repository

* install pip

* install venv package
 `pip install virtualenv`

 * install dependecies for the project `pip install -r requirements.txt`  


Main Script Usage (No Auth):

 * you must supply python3 environment with project's directory name instead of any file inside of the directory, `python3 [project-dir] [deviantart-username]`

   usage if in the main directory `python3 __main__.py deviantart-username`

   > Example: `python3 __main.py hyanna-natsu`

* optional argument `--filetype`

  usage `python3 __main__.py deviantart-username --filetype png`

  > Example: `python3 __main.py hyanna-natsu --filetype png`

**NOTE:** username is case-sensitive and it is the title of the user's page not the last part of the URL    
<br />

Alt Script Usage (Auth):  
This script **requires** for you to have your "client_id" & "client_secret" configured in **config.ini**.

> 1. Make an account with [deviantart](https://www.deviantart.com/join/)
>
> 2. get your "client_id" & "client_secret" [Here](https://www.deviantart.com/developers/apps)
>
> 3. Follow This [Guide](https://www.wfdownloader.xyz/blog/how-to-bulk-download-deviantart-images-and-videos-via-api) if its to complicated (follow along till step 6)
>
> 4. now copy your "client_id" & "client_secret" to **config.ini**.
>    should look like this:
>
>    > [credentials]  
>    > client_id = YOURID  
>    > client_secret = YOURSECRETKEY  
>
>    make sure its your actual ID & Key.

*A key might be allready provided, if its expired, get your own following above steps*.

Be sure to rename **config_TEMPLATE.ini** to **config.ini**.

- open a terminal/powershell window in the cloned directory if you havent allready.

- run the script as follows `python3 deviantart.py deviantart-username ` to download users main gallery like No Auth Script.

  > Example: `python3 deviantart.py hyanna-natsu`

#### Commands:

`--help` Brings up the help page   

`--filetype` Specify the filetype you wish to downlaod as (jpg, png, etc...)   

> `python3 deviantart.py hyanna-natsu --filetype png`

`--list` Lists the user's gallery folders to be used with `--folder` option.    

> Example: `python3 deviantart.py hyanna-natsu --list`

`--folder` Using the folder ID you get from `--list` you can specify the folder ID you wish to download.

> Example: `python3 deviantart.py hyanna-natsu --folder FE7E3825-13A5-9FAC-A7A7-A188ACC39877` Downloads Kemonomimi Folder.

`--all` Downloads everything, entire gallery and all folders.

`--collection` Downloads all images from the author's collection.    

> Example: `python3 deviantart.py hyanna-natsu --collection`
