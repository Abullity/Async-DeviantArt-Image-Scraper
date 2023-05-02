# Async-DeviantArt-Image-Scraper
Script takes DeviantArt username and scrapes artist's images asynchronously

Usage:
* clone the repository

* cd to the cloned repository

* install pip

* install venv package
 `pip install virtualenv`
 
 * install dependecies for the project `pip install -r requirements.txt`

 * you must supply python3 environment with project's directory name instead of any file inside of the directory, `python3 [project-dir] [deviantart-username]`

   * usage if in the main directory `python3 __main__.py deviantart-username`

     > Example: `python3 __main.py hyanna-natsu`

* optional argument `--filetype`

  *  usage `python3 __main__.py deviantart-username --filetype png`

    > Example: `python3 __main.py hyanna-natsu --filetype png`


NOTE: username is case-sensitive and it is the title of the user's page not the last part of the URL

