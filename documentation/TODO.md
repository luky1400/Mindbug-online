# Author’s TODO list and notes

## TODO - backend

- Add tests regularly for things that are not working
- Simplify and unify code
- Investigate if logs make sense - is order correct? ... Add log "Player 1" attacks.
  - Why "Ongoing effects recalculated." is twice in logs?  
  Player 2 declines to use Mindbug.
  Ongoing effects recalculated.
  Ongoing effects recalculated.

## TODO - frontend

- TODO - fix - full cards in battlefields are not visible, neither all icons
- Do not show Play button if no cards to be played (even if you cannot play card from hand because of ongoing effect), and do not show attack button if no cards to attack with (even if you cannot attack because of ongoing effect)
  - Also, show only Attack or End turn button when FRENZY card can attack again
- [Inspiration](https://www.google.com/search?q=mindbug+sharkdog+kills+target+before+combat&sca_esv=a02f3e9b87f4a5a7&biw=928&bih=929&sxsrf=ANbL-n7HQ14P5EW6K1BdKcbbh2tpTjZctA%3A1774706171802&ei=-93HabrZML6N-d8Py-v86A0&ved=0ahUKEwj6ws3X38KTAxW-Rv4FHcs1H90Q4dUDCBE&uact=5&oq=mindbug+sharkdog+kills+target+before+combat&gs_lp=Egxnd3Mtd2l6LXNlcnAiK21pbmRidWcgc2hhcmtkb2cga2lsbHMgdGFyZ2V0IGJlZm9yZSBjb21iYXQyBRAhGKABMgUQIRigAUiAX1CkC1iPXnABeACQAQCYAYYBoAGVFaoBBDE5Ljm4AQPIAQD4AQGYAhygArsVwgIIEAAYsAMY7wXCAgsQABiABBiwAxiiBMICCBAAGBYYChgewgIFEAAY7wXCAggQABiABBiiBMICBxAhGKABGAqYAwCIBgGQBgWSBwUxNy4xMaAHk1-yBwUxNi4xMbgHtxXCBwYxLjIzLjTIBzmACAA&sclient=gws-wiz-serp#fpstate=ive&vld=cid:9515da25,vid:kjw0N0Uhvm8,st:0)
- zlepšit zobrazení actual strength - stejně změnit i number of copies
- Smazat Close button u Card preview?
- Show Mindbug icon somewhere
- Improve Whaetl_e choosing number appearance.
- enhance UI - change colours, ..
- Special effects:
  - when card is defeated
  - when card is discarded
  - drawing cards
  - Hunt/No hunt
  - Hrac utoci
  - Aktivovala se akce
  - Zesnovačka zrušila PLAY akci, ..

## Bugs - backend

- When each player has Hyenix in discard pile and both lose life simultaneously. Player who is on turn must decide which player resolves Hyenix choice first.
  - this situation probably cannot happen

## Bugs - frontend

- For cards with purple border, I dont see that they are selected when being clicked.
- I can select card as defender when Turf the surfer forbits it from defending

## TODO - game rules

- Jiný naming:
  - keywords instead of special_types
  - efekty schopnosti: Příchod, ..
  - Stálé schopnosti (př. Zesnovačka)
  - do své herní oblasti
  - support i pro Češtinu
- Udělat funkce pro tyhle termíny: Odložit, Ovládnout nestvůru
- (Síla nestvůry nemůže mít nikdy nižší hodnotu než 1, a to ani v případě, že by některé efekty hodnotu síly upravovaly.)

## Nice to have

- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem. V případě shody tento proces opakujte."
- Když defender vybira, jestli a cim bude branit, tak zvyraznit utocici kartu:
  - Prompt: can you make orange/red border/glow to card that was selected as attacker. This border should only be applied until defender is selected.
- add other cards from different sets:
  - BEYOND ETERNITY, BATTLEFRUIT KINGDOM
  - Need to adjust frontend accordingly. E.g.: purple border for Jazz dog, Pandamme. Badges for new ongoing effects.
- Attack, play_card, End turn button - lepší by bylo místo click buttons, přetahovat
- add persistent database-backed sessions so rooms survive server restarts.
- add Time limit for action - 1 min
- (dát na rozklikávatko (vpravo nahoře) pro pravidla)

