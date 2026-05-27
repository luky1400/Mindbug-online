# Author’s TODO List

## TODO - backend

- Add tests regularly for things that are not working
- Simplify and unify code
- Investigate if logs make sense - is order correct? ... Add log "Player 1" attacks.
  - Player 2 declines to use Mindbug.
  Ongoing effects recalculated.
  Ongoing effects recalculated.
  - Waiting for Player 1 to choose enemy creatures to take control of with Harpy Mother.
  Player 1's Harpy Mother is defeated and triggers its DEFEATED action.
  Ongoing effects recalculated.
  Ongoing effects recalculated.
  Ongoing effects recalculated.
  Ongoing effects recalculated.
  Turn passes to Player 1.
- Implement: Pudl, (+ Slugapult, Alien_brain)
- delete action_types attribute from Card and use rather card.trigger_play_effect(self), ..
- Optionally use only one giraffe
- Test if deployment works fine:
  - add /health endpoint? - for Render
  - make game faster?

## TODO - frontend

- show visualization effect of discarded cards from hand for longer time + 1s (I dont have enough time to look at them properly)
- make cards nicer so it is readable well - texty se tam asi nejak dotahnou oddelene a strenth a nazev take
- Adjust UI layout to screen size
- Longer logs history/ add scrolling?
- enhance UI - change colours, choosing windows, ..
- (visualization effects for: Zesnovačka zrušila PLAY akci, Jazz_dog took control of cards)

## Bugs - backend

- Sometimes, Harpy_mother steals cards with strength above 5 except to 5!! when defeated when it attacked - very strange
- (When each player has Hyenix in discard pile and both lose life simultaneously. Player who is on turn must decide which player resolves Hyenix choice first. - this situation probably cannot happen)

## Bugs - frontend

- dont make cards_laid_out blick

## TODO - game rules

- Síla nestvůry nemůže mít nikdy nižší hodnotu než 1, a to ani v případě, že by některé efekty hodnotu síly upravovaly.
- Jiný naming:
  - keywords instead of special_types
  - efekty schopnosti: Příchod, ..
  - Stálé schopnosti (př. Zesnovačka)
  - do své herní oblasti
  - support i pro Češtinu - problem I dont have czech cards
- Udělat funkce pro tyhle termíny: Odložit, Ovládnout nestvůru

## Nice to have

- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem. V případě shody tento proces opakujte."
- Smazat Close button u Card preview?
- add other cards from different sets:
  - BEYOND ETERNITY, BATTLEFRUIT KINGDOM
  - Need to adjust frontend accordingly. E.g.: purple border for Jazz dog, Pandamme. Badges for new ongoing effects.
- add persistent database-backed sessions so rooms survive server restarts.
- add Time limit for action - 1 min
- (dát na rozklikávatko (vpravo nahoře) pro pravidla)

