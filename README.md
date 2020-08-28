# MadLibs
An original Discord bot that lets you play MadLibs with your friends (or by yourself if you don't have any friends)

Note: My code can be messy and I'm only 13, so if you want to ~~roast~~ review me, you can send feedback using the `ml!feedback` command.
## Inviting
You can invite MadLibs [here](https://discord.com/api/oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot)
This invite link comes equipped with all the permissions it needs.
## Setup
I don't know why you would want to run an instance of this bot, but all you have to do is:
- Create a file called `config.py` in the root directory
- Inside it, put `TOKEN = 'your bot token'`
- Open up command prompt, go in this directory, then type `python bot.py`
## Commands
There are only a few commands on MadLibs. The prefix defaults to `ml!`, but you may customize it.
### - ml!prefix <prefix>
This command changes the current guild prefix if the prefix argument is provided. If not, it will display the current guild prefix.
- Permissions required: `Manage Server`
### ml!feedback <your feedback>
This command lets you give feedback about anything related to the bot, including the code on this repository. You can comment about anything, and give constructive criticism.
### - ml!madlibs
This command starts a MadLibs game, with the user who invoked the command as the host. Anyone can join these games by typing `join` at any point of the process.
### - ml!custom <subcommand>
This command contains a variety of subcommands, all having to do with custom story templates
#### ml!custom add <name> <story template>
This subcommand adds a custom template to the guild. You do not need any permissions to do this, although the story template must have at least one *blank*, like `{noun}`.
#### ml!custom remove <name>
This subcommand removes a custom template from the guild. You need the `Manage Server` permission to use this, however.
- Permissions required: `Manage Server`
#### ml!custom edit <name> <new story template>
This subcommand edits an existing custom template in the guild. To edit your own template, you do not need any permissions but to edit others, you need the `Manage Server` permission.
#### ml!custom all
This subcommand lists all the names of the custom templates in the current guild.

That's all, I hope you enjoy this bot!