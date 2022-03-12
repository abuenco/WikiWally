# About the Project

WikiWally is a Discord Bot that retrieves Wikipedia articles using the PyMediaWiki Python wrapper for the MediaWiki API. Users can input commands accompanied by a query to find the article that most closely matches it. Users who are feeling more adventurous can also retrieve one to ten random articles.

The Wikpedia article retrieved by the bot is displayed in a Discord embed in the channel where the command was executed:

![page_sample_arashi](https://user-images.githubusercontent.com/25872191/158001111-83f5423e-716b-40cf-97ad-654c1e997fa0.png)  

This is what you get when you enter ```.wiki page arashi``` in a Discord channel!

WikiWally is hosted online on [Heroku](https://www.heroku.com/home)... for free, so it's running on one (free) web dyno.

## Bot Commands
|      Command     | Description |
|------------------| ------------|
| ```.wiki page``` | Fetches a article given user input.|
| ```.wiki random``` | Fetches a random Wikipedia article.|
| ```.wiki random N ```| Fetches N random Wikipedia articles, where _N_ is an integer from 1 to 10.|
| ```.wiki options```| Provides query suggestions, which may be helpful if you can't find the article you're looking for with ```.wiki page```.|


## Software
- [Python](https://www.python.org/)
- [Discord py](https://discordpy.readthedocs.io/en/stable/)
- [PyMediaWiki](https://pymediawiki.readthedocs.io/en/latest/)

## Contact
Andie Buenconsejo  
Email: al.buenco@gmail.com  
[Project Link](https://github.com/abuenco/WikiWally)




