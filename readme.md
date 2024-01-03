# Pornhub Auto Download

This plugin will automatically download videos from Pornhub.com when a scene is created and its URL is a valid Pornhub URL.

# How to install

1. Run `pip install -r requirements.txt` to install the required packages
2. Download the zip of the repository
3. Extract `ph_auto.yml` to your Stash plugins folder
4. Create a folder called `py_plugins` in your Stash plugins folder
5. Extract `ph_auto.py` and `log.py` to the `py_plugins` folder
6. Once that is done, reload your plugins in Stash to load the plugin


# How to use

1. Create a scene with a valid Pornhub URL
2. Wait for the scene to be created
3. The video will be downloaded to the folder you specified in the plugin settings (this can take a while but the progress is logged and can be seen in the Stash logs)
4. Once downloaded, a scan is triggered to add the file to the database
5. The 2 scenes will be merged and generate will be called on the scene
6. Done!


# Thanks

Thanks to [niemands](https://github.com/niemands/StashPlugins) for his log file as well as who I got the idea for the plugin from.