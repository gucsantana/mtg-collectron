# mtg-collectron

Magic: the Gathering collection tracker website, developed with Vue 3 and Vuetify. I like visual representations of things, so I built this tool for myself.
There are tons of arguably better, more efficient tools out there, like DelverLens, but hey.

# Features

Tracks cards for each set in the game, including promo sets, tokens and all that. Can track amount per card, and whether foil or not.
No distinction between multiple copies of the same card, because that's not the point here. Use Moxfield or something for that.
Up to four separate tags per card, also indicated in Card Finder. You can use them to track cards in foreign languages, or in your trade binder, or whatever else.

Card search to filter through cards in a set, set search to filter through the list of sets (matches either set name or set code).

Allows users to import cards with the Moxfield export syntax, or export and import their entire collection as JSON-stringified text.
Storage is local, no plans for adding accounts or databases.

'Card Finder' checks which versions of a card you have in your stock, if any.

'Decklist Finder' reads a passed decklist and returns all cards in that list found in your storage, prioritizing oldest or newest prints, in the amount requested.

# Upcoming Features and Improvements

Scrolling to top on page change (why is it so hard? lol)

More filters for Decklist Finder, allow user to pass Moxfield url

'Stats' screen with information and trivia about the collection

Precalculated percentages so we can use them outside of the set context

# Known Issues

I don't -fully- trust the collection percentages yet, it's very much reverse-engineered and with a lot of guessing and fiddly counters.

Some cards on Decklist Finder seem to return lower counts than you actually have of them. Weird.

Tidy Up Collection produces weird results for older sets with multiple prints of the same card, like Alliances and CHK (because of Brothers Yamazaki)

# Pages Deployment

Run "npm run deploy". Branch gh-pages is set up to automatically publish to the Github pages when committed to.