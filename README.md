MoobieTime is a bot to manage suggestions for weekly movie nights! Suggesting a movie successfully will add it to a database. 
Suggesting a movie that is already on the list will redirect you to the message containing a link with the tvdb.com page for the movie in question. 
The bot listens for heart reactions to update reaction count for the /topmovies command. 
Those with your designated admin role will be able to add a check mark (:white_check_mark:) reaction to mark a movie as watched 
on the back end, and provide a way for the user to see that the movie has already been watched. 
All commands will work with either the designated prefix (&\<command>), 
adjustable in your config.json, or /\<command><br><br>
**List of available commands:**<br><br>
**/suggest \<search string>** - Suggest a movie by searching the website for the top 5 results, select the movie with the buttons that show up on the bottom of the interaction message to add it to the database and suggestion channel.\
**/suggestlink \<link>** - Suggest a movie directly with the link to the relevant thetvdb.com page.\
**/topmovies (#)** - Get a list of the top (#) unwatched movies currently in the database, ranked by reaction count.<br><br>
**Admin Commands:**<br><br>
**/removemovie \<movie name>** - Finds and removes a movie from the database\
**/addmovie \<movie title> \<movie link> (year)** - Force adds a movie with the given title and link (can be to any url). Several optional commands are present, 
none but the year should be given any value as they are there to provide defaults to pass down to the functions on the back end.<br><br>
**Config file layout:**<br><br>
```
{
    "cogs": ["cogs.user_cog", "cogs.admin_cog"],
    "embed_color": "000000",
    "cmd_prefix": "&",
    "token": "Bot token",
    "admin_role": "Role ID of your designated admin role",
    "database_path": "Path to your local db",
    "tvdb_key":  "Your TVDB api key",
    "suggest_channel": "Channel ID for your designated suggestion channel",
    "target_channel": "Channel ID for the channel you'd like the bot output to go in"
}
```
[Metadata provided by TheTVDB. Please consider adding missing information or subscribing.](https://thetvdb.com/subscribe)