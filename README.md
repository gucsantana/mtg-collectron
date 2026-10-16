# mtg-collectron

Magic: the Gathering collection tracker website, developed with Vue 3 and Vuetify. I like visual representations of things, so I built this tool for myself.
There are tons of arguably better, more efficient tools out there, like DelverLens, but hey.

# Features

Tracks cards for each set in the game, including promo sets, tokens and all that. Can track amount per card, and whether foil or not.
No distinction between multiple copies of the same card, because that's not the point here. Use Moxfield or something for that.
Up to four separate tags per card, also indicated in Card Finder. You can use them to track cards in foreign languages, or in your trade binder, or whatever else.

Card search to filter through cards in a set, set search to filter through the list of sets (matches either set name or set code).

Allows users to import cards with the Moxfield export syntax, or export and import their entire collection as JSON-stringified text.
Users must sign in or create an account before entering the collection. Authentication is handled by the Spring Boot backend; the collection and preferences continue to be stored in the browser's local storage.

'Card Finder' checks which versions of a card you have in your stock, if any.

'Decklist Finder' reads a passed decklist and returns all cards in that list found in your storage, prioritizing oldest or newest prints, in the amount requested.

# Local Development

Run the Spring Boot backend at `http://localhost:8080`, then start the frontend with `npm run dev`. Vite proxies `/mtg-collectron` API requests to the backend so the browser does not make a cross-origin request. The authentication endpoints expected by the frontend are:

- `GET /mtg-collectron/auth/session` returns the current public user as JSON, or HTTP 401 when no valid session exists.
- `POST /mtg-collectron/auth/login` accepts `{ "email": "...", "password": "..." }`.
- `POST /mtg-collectron/auth/register` accepts `{ "email": "...", "username": "...", "password": "..." }`.
- `POST /mtg-collectron/auth/logout` invalidates the current session.

Successful login and registration responses should return the public user profile (or `{ "user": { ... } }`) and set an HttpOnly session cookie. Do not return `password_hash`; the backend must validate fields, enforce the unique email and username constraints, hash passwords, and manage session cookies. In production, serve the API over HTTPS and make it same-origin with the frontend so cookie credentials remain protected. If your backend is configured for HTTPS in development, change the proxy target in `vite.config.js` to `https://localhost:8080`.

# Upcoming Features and Improvements

Scrolling to top on page change (why is it so hard? lol)

More filters for Decklist Finder, allow user to pass Moxfield url

'Stats' screen with information and trivia about the collection

# Known Issues

I don't -fully- trust the collection percentages yet, it's very much reverse-engineered and with a lot of guessing and fiddly counters.

Some cards on Decklist Finder seem to return lower counts than you actually have of them. Weird.

# Pages Deployment

Run "npm run deploy". Branch gh-pages is set up to automatically publish to the Github pages when committed to.