# Brief author’s notes for internal purposes

## TODO - backend

- Add tests regularly for things that are not working
- Simplify and unify code
- Investigate if logs make sense - is order correct? ... Add log "Player 1" attacks.
- TODO - Implement - Wheatl_e, ..

## TODO - frontend

- Do not show Play button if no cards to be played (even if you cannot play card from hand because of ongoing effect), and do not show attack button if no cards to attack with (even if you cannot attack because of ongoing effect)
- [Inspiration](https://www.google.com/search?q=mindbug+sharkdog+kills+target+before+combat&sca_esv=a02f3e9b87f4a5a7&biw=928&bih=929&sxsrf=ANbL-n7HQ14P5EW6K1BdKcbbh2tpTjZctA%3A1774706171802&ei=-93HabrZML6N-d8Py-v86A0&ved=0ahUKEwj6ws3X38KTAxW-Rv4FHcs1H90Q4dUDCBE&uact=5&oq=mindbug+sharkdog+kills+target+before+combat&gs_lp=Egxnd3Mtd2l6LXNlcnAiK21pbmRidWcgc2hhcmtkb2cga2lsbHMgdGFyZ2V0IGJlZm9yZSBjb21iYXQyBRAhGKABMgUQIRigAUiAX1CkC1iPXnABeACQAQCYAYYBoAGVFaoBBDE5Ljm4AQPIAQD4AQGYAhygArsVwgIIEAAYsAMY7wXCAgsQABiABBiwAxiiBMICCBAAGBYYChgewgIFEAAY7wXCAggQABiABBiiBMICBxAhGKABGAqYAwCIBgGQBgWSBwUxNy4xMaAHk1-yBwUxNi4xMbgHtxXCBwYxLjIzLjTIBzmACAA&sclient=gws-wiz-serp#fpstate=ive&vld=cid:9515da25,vid:kjw0N0Uhvm8,st:0)
- Když defender vybira, jestli a cim bude branit, tak mu ukazat kartu utocnika - zvyraznit ji:
  - Prompt: can you make orange/red border/glow to card that was selected as attacker. This border should only be applied until defender is selected.
- udělat nejakou signalizaci/Iconu, která upozorní hrace, ze je na tahu/dela akci?
- Smazat Close button u Card preview?
- Special effects:
  - when card is defeated
  - drawing cards
  - Hunt/No hunt
  - Hrac utoci
  - Aktivovala se akce
  - Zesnovačka zrušila PLAY akci, ..

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

- Attack, play_card, End turn button - lepší by bylo místo click buttons, přetahovat
- add persistent database-backed sessions so rooms survive server restarts.
- add Time limit for action - 1 min
- add other cards from different sets:
  - BEYOND ETERNITY, BATTLEFRUIT KINGDOM
  - Need to adjust frontend accordingly. E.g.: purple border for Jazz dog, Pandamme. Badges for new ongoing effects.
- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem.
V případě shody tento proces opakujte."
- dát na rozklikávatko (vpravo nahoře): pravidla
- Ukazat pouze horni pulku karet v ruce?
- Kdyz zahraju kartu a cekam na opponenta, jestli pouzije Mindbug, tak kartu dát doprava doprostred, stejne jako v Mindbug online?

## Bugs - backend

- 

## Bugs - frontend

- Opponents cards laid out can be selected for target attack but they have no blue border when selected!
- In Knightmare, Steamforger cards, I dont see green actual strength if it is higher than normal.
- I see FRENZY above Hyenix card when deciding whether to play it or not.
- End turn button should disappear immediatelly after clicking 2nd attack button

