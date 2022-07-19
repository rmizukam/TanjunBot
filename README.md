# Discord Bot made with tanjun-hikari API
Converted my old bot that is for me and my friends to have fun with on discord.

# Documentation
https://www.hikari-py.dev/hikari/index.html

https://github.com/tandemdude/hikari-lightbulb

A good read on how to implement more features can come from:

https://patchwork.systems/programming/hikari-discord-bot/introduction-and-basic-bot.html

# Virtual Environments
I want to get used to Virtual Environments since they are apparently very  useful. This bit will also help with that.
Basic Steps to creating and using venv's are:

In Terminal/Command prompt, type:
python -m venv env

'venv' is used to create the virtual environment and 'env' is the name of the virtual environment.
# Discord Bot made with Hikari API
Converted my old bot that is for me and my friends to have fun with on discord.

# Documentation
https://www.hikari-py.dev/hikari/index.html

https://github.com/tandemdude/hikari-lightbulb

A good read on how to implement more features can come from:

https://patchwork.systems/programming/hikari-discord-bot/introduction-and-basic-bot.html

# Virtual Environments
I want to get used to Virtual Environments since they are apparently very  useful. This bit will also help with that.
Basic Steps to creating and using venv's are:

In Terminal/Command prompt, type:
python -m venv env

'venv' is used to create the virtual environment and 'env' is the name of the virtual environment.

# To Activate the Virtual Environment

MacOS/ Linux:

source env/bin/activate

Windows:

./env/Scripts/activate

once activated you continue as normal

If bot doesnt work due to a certificate error

https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python

# Packages Needed to Run the Bot
pip install python-dotenv

from dotenv import load_dotenv

load_dotenv()

Need to install hikari

MacOS:

python -m pip install -U hikari

Windows:

py -3 -m pip install -U hikari

will need to install a command handler when using commands with hikari bot

pip install hikari-lightbulb

or

pip install hikari-tanjun

# Some Other Notes
Content for images and video are not mine

Important link for creating discord bots: https://discord.com/developers/applications/

Note on Variables that are in ALL CAPS (.env variables):
Discord bots have an identifying token to allow you to edit settings and other behavior of the bot. If you are hosting locally/ are not worried about others knowing the code you can make it public. When not hosting locally it is recommended to create environment variables to create a "secret variable" that others do not have access to even if they have the source code. The replit.com site allows you to do this without creating a separate file to save these keys in.
When hosting locally, you can create a file called ".env" and format data as VARNAME='information'. You can then use the python-dotenv package to import data from these files. Additionally, you can exclude the uploading of these files to github by adding *.env to your .gitignore file.

# To Activate the Virtual Environment

MacOS/ Linux:
source env/bin/activate

Windows:
./env/Scripts/activate

once activated you continue as normal

If bot doesnt work due to a certificate error

https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python

# Some Other Notes
Content for images and video are not mine

Important link for creating discord bots: https://discord.com/developers/applications/

Note on Variables that are in ALL CAPS (.env variables):
Discord bots have an identifying token to allow you to edit settings and other behavior of the bot. If you are hosting locally/ are not worried about others knowing the code you can make it public. When not hosting locally it is recommended to create environment variables to create a "secret variable" that others do not have access to even if they have the source code. The replit.com site allows you to do this without creating a separate file to save these keys in.
When hosting locally, you can create a file called ".env" and format data as VARNAME='information'. You can then use the python-dotenv package to import data from these files. Additionally, you can exclude the uploading of these files to github by adding *.env to your .gitignore file.
