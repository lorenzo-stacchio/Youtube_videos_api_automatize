# Automatize youtube channel stuff 

## Google cloud API activations
Go to https://console.cloud.google.com/ and create a novel application.

Now go to the credential page and set an API key and n ID client Oauth 2.0.

In Oauth consensus insert the mail of the google account that will be used by your application.

Download the client secret file from the Oauth 2.0, rename it credentials.json and put it in the root folder.

Then, execute quickstart.py.

This would create the "token.json" file, which should be used to run the main script which is "automatize_like_comment_add.py".

For that application, create also a "comment_template.txt" file and a "playlistId.txt" file which contains respectively the comment template and the id of the playlist to add the videos.




## Get secret token


## Run automatization script with authentication


## TODO

Check if the comment was effectively inserted. Otherwise ban the channel id and store it in some local dictionary. 