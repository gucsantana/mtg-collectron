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

# Upcoming Features and Improvements

Some manner of "find these cards for me" deck builder helper

Tightening up the code for edge cases

# Known Issues

Clicking 'Close' on Card Finder without text seems to crash it. How did I not see that before? Lol.

Certain sets, like 'Universes Within', load no cards. Not sure what I need to add to the syntax.

Certain sets, like 'Lost Caverns of Ixalan', have weeeeeird numbering, and thus the displayed order is not the same as the numbered order.

There are also many one-off sets that have unique rules, like 'Modern Horizons 2 Timeshifts' being technically its own set separated from both MH2 and MH3 and being only available from collector boosters (so it doesn't fit the usual filtering in any way). Card numbering, base set/extra cards split, and collection percentages could end up wrong because of this. Just roll with it.

I don't -fully- trust the collection percentages, it's very much reverse-engineered and with a lot of guessing and fiddly counters.

# Pages Deployment

Run "npm run deploy". Branch gh-pages is set up to automatically publish to the Github pages when committed to.