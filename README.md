# SignedMTG Scraper
A selenium script to find and save signed/graded/altered MTG card listings from TCGPlayer.

## Dependencies
Python 3.11.9 (Later versions should work but this is what I use
Google Chrome (Latest Version)
Something to open `.xlsx` files (you can use Google Sheets iirc)

### Required Python Libraries:
```
selenium
xlsxwriter
requests
colorama
```

> If you follow my installation tutorial all these libraries will be installed through requirements.txt

## Installation
1. Install python3 and google chrome if you haven't already 
2. Download and extract this repository
3. Rightclick anywhere in the extracted folder and click "Open in Command Prompt"
4. Run `pip install -r requirements.txt` to install all necessary libraries
5. Done! You can now run `python main.py --help` to see what arguments you can use or read the argument documentation below!
> all outputs from the scraper will be put into an xlsx file in the same folder as the script

## Example Usage
`python main.py -s 43db324c -c Green -t Creature`
This command will scan listings for all green creatures from the seller with the seller ID '43db324c'.

`python main.py -n "lightning bolt" -c Red`
This command will scan listings for all red cards with lightning bolt in their text.

`python main.py -r Mythic -a -g`
This command will scan listings for all mythic cards, including searching for alters and graded cards.

## Scraper Arguments
Add as many arguments as you'd like to the command `python main.py` to get a smaller search!

### -h (--help)
The help command.
Example command: `python main.py -h`
### -n (--name)
Search for a card by name. Place quotation marks around this query.
Example command: `python main.py -n "palladium myr"`
### -c (--color)
Search for a card by color. Acceptable values are White, Blue, Black, Red, Green, Colorless
Example command: `python main.py -c Colorless`
### -s (--seller)
Search for a card by tcgplayer Seller ID. Go to the feedback page of the seller you want, and their seller ID will be in the URL (ex. 43db324c).
Example command: `python main.py -s 43db324c`
### -t (--type)
Search for a card by card type. Acceptable values are Creature, Artifact, Legendary, Land, Instant, Sorcery, Enchantment, Planeswalker
Example command: `python main.py -t Artifact`
### -r (--rarity)
Search for a card by rarity. Acceptable values are Common, Uncommon, Rare, Mythic, Special, Token, Land, Promo
Example command: `python main.py -r Rare`
### -a (--altered)
Add the filters for altered cards to the task. Will add "alter" to the filter words.
Example command: `python main.py -a`
### -g (--graded)
Add the filters for graded cards to the task. Will add "bgs", "cgc", "psa", "graded" to the filter words.
Example command: `python main.py -g`
### -v (--verbose)
Meant for development, adds extra debug logs to the command line
Example command: `python main.py -v`

