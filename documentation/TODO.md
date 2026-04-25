# Author’s TODO list and notes

## TODO - backend

- Add tests regularly for things that are not working
- Simplify and unify code
- Investigate if logs make sense - is order correct? ... Add log "Player 1" attacks.
  - Why "Ongoing effects recalculated." is twice in logs?  
  Player 2 declines to use Mindbug.
  Ongoing effects recalculated.
  Ongoing effects recalculated.
- Implement: Jazz_dog, Ratomanger, Slugapult (+ Alien_brain)

## TODO - frontend

(I want the same effect as when card is played as when it is stolen by Mindbug - green glow?)

(Zesnovačka zrušila PLAY akci, ..)

- make cards nicer so it is readable well - texty se tam asi nejak dotahnou oddelene a strenth a nazev take
- Adjust UI layout to screen size
- Longer logs history/ add scrolling?
- enhance UI - change colours, choosing windows, ..

## Bugs - backend

- (When each player has Hyenix in discard pile and both lose life simultaneously. Player who is on turn must decide which player resolves Hyenix choice first. - this situation probably cannot happen)

## Bugs - frontend

- 

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

