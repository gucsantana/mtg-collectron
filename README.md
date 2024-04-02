# mtg-collectron

Magic: the Gathering collection tracker website, developed with Vue 3 and Vuetify. I like visual representations of things, so I built this tool for myself.
There are tons of arguably better, more efficient tools out there, like DelverLens, but hey.

# Features

Tracks cards for each set in the game, including promo sets, tokens and all that. Can track amount per card, and whether foil or not.
No distinction between multiple copies of the same card, because that's not the point here. Use Moxfield or something for that.

Card search to filter through cards in a set, set search to filter through the list of sets (matches either set name or set code).

Allows users to import cards with the Moxfield export syntax, or export and import their entire collection as JSON-stringified text.
Storage is local, no plans for adding accounts or databases.

'Card Finder' checks which versions of a card you have in your stock, if any.

# Upcoming Features and Improvements

Logos, introductory text and other such niceties.

Better formatting on mobile.

# Known Issues

Certain sets, like 'Universes Within', load no cards. Not sure what I need to add to the syntax.