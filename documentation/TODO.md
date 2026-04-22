# Author’s TODO list and notes

## TODO - backend

- Add tests regularly for things that are not working
- Simplify and unify code
- Investigate if logs make sense - is order correct? ... Add log "Player 1" attacks.
  - Why "Ongoing effects recalculated." is twice in logs?  
  Player 2 declines to use Mindbug.
  Ongoing effects recalculated.
  Ongoing effects recalculated.
- Implement: Jazz_dog, Ratomanger, Slugapult

## TODO - frontend

- Do not show Play button if no cards to be played (even if you cannot play card from hand because of ongoing effect), and do not show attack button if no cards to attack with (even if you cannot attack because of ongoing effect)
  - Also, show only Attack or End turn button when FRENZY card can attack again
- Když defender vybira, jestli a cim bude branit, tak zvyraznit utocici kartu:
  - Prompt: can you make red dashed border/glow to card that was selected as attacker. This border should only be applied until defender is selected.

- make crads nicer so it is readable well - texty se tam asi nejak dotahnou oddelene a strenth a nazev take
- enhance UI - change colours, choosing windows, ..
- Add scrolling to logs?
- Adjust UI layout to screen size
- Special effects:
  - when card is defeated
  - when card is discarded
  - drawing cards
  - Hunt/No hunt
  - Hrac utoci
  - Aktivovala se akce
  - Zesnovačka zrušila PLAY akci, ..

## Bugs - backend

- 

- (When each player has Hyenix in discard pile and both lose life simultaneously. Player who is on turn must decide which player resolves Hyenix choice first. - this situation probably cannot happen)

## Bugs - frontend

- When card is greyed out, I cannot see badges - FRENZY, etc.

## TODO - game rules

- Síla nestvůry nemůže mít nikdy nižší hodnotu než 1, a to ani v případě, že by některé efekty hodnotu síly upravovaly.
- Jiný naming:
  - keywords instead of special_types
  - efekty schopnosti: Příchod, ..
  - Stálé schopnosti (př. Zesnovačka)
  - do své herní oblasti
  - support i pro Češtinu
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

