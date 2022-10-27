# Sevenβ Discord Bot
A discord bot for 7Span's server. This bot is created using Discord API and ClickUp API. It has the following features
- Employees can get details of ClickUp task hours
- Gives monthly summary of ClickUp hours
- Birthday and work anniversary messages in the celebration channel
- Gives notification of newly joined users to Harsh Kansagra
- Send every day report of employees' logged hours to HR in XML file format
- Creates morning and evening threads in given discord channels for EOD report
- Broadcast command for the broadcasting message to each user via DM
- Sends random memes of a given category
- Sends random facts about the world
- Provides help manual


## Installation
### Create discord application in developer portal
1. Open the [Discord developer portal](https://discord.com/developers/applications) and log into your account.
2. Click on the "New Application" button.
3. Enter a name and confirm the pop-up window by clicking the "Create" button.
4. Navigate to Bot menu from left side menubar
5. Add one Bot and setup access token then store it somewhere for later use
6. Navigate to OAuth2 > URL Generator from left side menubar
7. Select Bot in scopes field and tick below options in permission field
<img src='imgs/1.png'/>
8. Then copy generated URL and paste it in browser then invite your Bot to your sever.

### Now you have to setup project
1. Install Python3.x in your machine
2. Clone this repository in your workspace
```shell
git clone https://github.com/parth-p-7span/discord-bot-python.git
```
3. Navigate to discord-bot-python folder in your terminal/CMD
```shell
cd discord-bot-python
```
4. Install required packages for the project using below command
```shell
pip install -r requirements.txt
```
5. Create a file in project root directory named with `.env` and add your credentials in that file. [Click here](https://gist.githubusercontent.com/parth-p-7span/147a289ae4111f77f816b2fcebf30ce5/raw/7a5a5bdc753b92c6f81b7cfe33aeacd245c482ab/temp.env) for example file.
6. Run the `main.py` file using following command.
```shell
python main.py
```