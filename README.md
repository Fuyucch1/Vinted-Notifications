# Vinted-Notifications

A telegram bot for real-time Vinted listing notifications/alerts. **Natively works on all Vinteds, no matter the country.**


⚠️ This is an early stage WIP. Expect bugs and missing features. ⚠️

## Table of Content

- [Introduction](#Introduction)
- [How to install](#How-to-install)
- [How to use](#How-to-Use)
- [How to update](#How-to-update)
- [Acknowledgements](#Acknowledgements)

## Introduction

This bot allows you to look for multiple items at the same time and to be notified when one of them is posted on Vinted.

## How to install

Project was made with Python 3.11.

1. Clone the repository or download the latest [release](https://github.com/Fuyucch1/Vinted-Notifications/releases/latest) and extract it.

2. Install the dependencies with pip

```
pip install -r requirements.txt
```

3. Fill the missing values in [`configuration_values.py`](configuration_values.py)

`TOKEN` can be obtained by creating a new bot with the BotFather on Telegram. [Learn how to create a bot here](https://core.telegram.org/bots/tutorial)\
`CHAT_ID` can be obtained by sending a message to the bot and then calling the `getUpdates` method on the Telegram API at this address :
```https://api.telegram.org/bot[TOKEN]/getUpdates```. Don't forget to replace `[TOKEN]` with your bot's token.

4. Run the bot with

```py
python telegram_bot.py
```

## How to use

After starting the bot, you can use the following commands on Telegram :

`/add_query query` - Adds a query to supervise.\
`/remove_query query_number` - Removes a keyword from the list.\
`/remove_query all` - Removes all keywords\
`/queries` - Get all queries\
`/hello` - Check if the bot is working\
`/create_allowlist` - Creates an allowlist of country of origin\
⚠️ Be aware that creating an allowlist will slow down the bot. ⚠️\
`/delete_allowlist` - Deletes the allowlist\
`/add_country XX` - Adds a country to the allowlist. Country must follow ISO3166 standard\
`/remove_country XX` - Removes a country from the allowlist\
`/allowlist` - Get the allowlist

## Quick example

```
/add_query https://www.vinted.fr/catalog?search_text=This%20is%20a%20test&time=1728936591&catalog[]=2309&price_to=150&currency=EUR&price_from=20&page=1
```

## How to update

1. Download the latest [release](https://github.com/Fuyucch1/Vinted-Notifications/releases/latest) and extract it.
2. Replace the old files with the new ones.
3. Don't forget to keep your tokens.
4. You can keep your vinted.db, except if the new release specifies otherwise.

This is an early stage WIP. There's no migration procedure planned between versions. I'll do it soon.

## Acknowledgements

Thanks to [@herissondev](https://github.com/herissondev) for maintaining pyVinted, a core dependancy of this project.
