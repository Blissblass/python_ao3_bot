# README

# Project: AO3 Discord Bot

This is an application that I built for a client from September 1st 2021 to October 5th  2021. The client directed the development, and I worked along with them to build the end product. The project was initially cancelled, however we started working on it again after a few weeks around October 2nd. Our main goal for this project was to create an app for the popular social messaging app [Discord](https://discord.com) that would check for updates on [AO3](https://archiveofourown.org) and notify you. [AO3](https://archiveofourown.org) is a non-profit open source website where you can share fictious stories about movies, shows, books etc.

# --THIS PROJECT IS RETIRED--

# Usage

The bot is very simple to start using, all you need is a [Discord](https://discord.com) account and a Discord Server in which you have enough permissions to invite users/bots.
After adding the bot to a server through [this link](https://top.gg/en/bot/882596640479936533), you can access all of its commands using ^help. To add a work, you just simply paste the desired work's url after calling ^add_work. This adds the work to the database and from now on it will be periodically checked for updates every 5 minutes.

To view all of your saved works, you can simply type ^get_all_works. This will display every single work you've saved, and also display their ID's so that you can also remove them if you want to.

# Challenges

One major challenge that I faced while building this app was figuring out how to periodically check for updates on every work. For this, I had to first figure out a database table setup that would fit the desired effect. I quickly came up with a solution, and created a table as such:

| works | values |
| --- | --- |
| id | integer |
| work_id | integer |
| chapters | integer |
| server_id | big_int |
| channel_id | big_int |
| user_id | big_int |

The update-checking works by initially saving the fetched chapter count to the database, and then fetching the chapter count again every 5 minutes and seeing if there's any changes, I initally wrote my own code for this, however after doing a bit of seraching I found that another person already built an API that fits the use of this proejct, so I used that instead. 
The update logic works like this: 
* If the new chapter count is higher than the saved count, inform the user, and then update the saved record. 
* If it's lower than the saved amount, this means a chapter was deleted, so silently update the count without informing the user. 
* Else, if it's still the same, do nothing.

The final challenge I faced for this app was figuring out how to asynchnorously run the update checking function so that it wouldn't clog up the application. After quickly skimming through some documentation, I used the @tasks helper to set this up as such:

```python

# Code for changing the applications status on Discord
@tasks.loop(minutes=5)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))   

# Code for checking all works saved to the database for any updates
@tasks.loop(minutes=5)
async def check_update():
  await check_all_for_update()
```

# To Do

I am currently planning on adding a function to search for works directly on Discord instead of having to get the URL from the browser, so that users can have a more easy and intelligible experience.

# Technologies used

This app was built with Python and uses [Discord.py](https://discordpy.readthedocs.io/en/stable/) and an [AO3 API that was built by Armindo Flores](https://github.com/ArmindoFlores/ao3_api).
