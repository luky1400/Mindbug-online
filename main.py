from base_classes import Game
from cards import get_card_pool
from enums import CardSpecialType
from enums import GameState


def print_game_state(game: Game) -> None:
    state = game.get_state()
    turn_player = game.current_player
    opponent = game.opponent

    def cards_to_text(cards: list, indexed: bool = False) -> str:
        if not cards:
            return "-"
        if indexed:
            return "\n".join(f"    {index}: {card.short_label()}" for index, card in enumerate(cards))
        return "\n".join(f"    - {card.short_label()}" for card in cards)

    print("\n" + "=" * 72)
    print(f"TURN: {state['turn_player']} | STATE: {state['game_state']}")
    if state.get("winner"):
        print(f"WINNER: {state['winner']}")
    print("-" * 72)

    print(f"[ON TURN] {turn_player.name}")
    print(
        f"  lives={turn_player.number_of_lives} | mindbugs_remaining={turn_player.mindbugs_remaining} | "
        f"hand_count={len(turn_player.hand)} | draw_pile_count={len(turn_player.draw_pile.cards)} | "
        f"discard_pile_count={len(turn_player.discard_pile)}"
    )
    hand_text = cards_to_text(turn_player.hand, indexed=True)
    board_text = cards_to_text(turn_player.cards_laid_out)
    discard_text = cards_to_text(turn_player.discard_pile)
    print(f"  hand:\n{hand_text}" if hand_text != "-" else "  hand: -")
    print(f"  board:\n{board_text}" if board_text != "-" else "  board: -")
    print(f"  discard_pile:\n{discard_text}" if discard_text != "-" else "  discard_pile: -")

    print()
    print(f"[OPPONENT] {opponent.name}")
    print(
        f"  lives={opponent.number_of_lives} | mindbugs_remaining={opponent.mindbugs_remaining} | "
        f"hand_count={len(opponent.hand)} | draw_pile_count={len(opponent.draw_pile.cards)} | "
        f"discard_pile_count={len(opponent.discard_pile)}"
    )
    opponent_board = cards_to_text(opponent.cards_laid_out)
    opponent_discard = cards_to_text(opponent.discard_pile)
    print(f"  board:\n{opponent_board}" if opponent_board != "-" else "  board: -")
    print(
        f"  discard_pile:\n{opponent_discard}"
        if opponent_discard != "-"
        else "  discard_pile: -"
    )


def choose_int(prompt: str, min_value: int, max_value: int) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw.isdigit():
            print("Please enter a number.")
            continue
        value = int(raw)
        if min_value <= value <= max_value:
            return value
        print(f"Please enter a number between {min_value} and {max_value}.")


def player_turn(game: Game) -> None:
    current = game.current_player
    opponent = game.opponent

    # If player has no creatures on board, force "Play card" action
    if not current.cards_laid_out:
        action = 1
        print(f"\n{current.name}, you have no creatures on the board. You must play a card.")
    else:
        print(f"\n{current.name}, choose action:")
        print("1) Play card")
        print("2) Attack")
        action = choose_int("Action: ", 1, 2)

    if action == 1:
        if not current.hand:
            print("No cards in hand, skipping to attack.")
            player_turn_attack(game)
            return
        print("\nYour hand:")
        for i, card in enumerate(current.hand):
            print(f"  [{i}] {card.short_label()}" + (f" - {card.description}" if card.description else ""))
        hand_idx = choose_int("Choose card index: ", 0, len(current.hand) - 1)

        use_mindbug = False
        if opponent.mindbugs_remaining > 0:
            # Opponent decides whether to use Mindbug on this card
            mb = input(f"{opponent.name} use Mindbug on this card? (y/n): ").strip().lower()
            use_mindbug = mb == "y"
        try:
            game.play_card(hand_idx)
            if game.game_state == GameState.AWAITING_MINDBUG:
                game.respond_to_mindbug(use_mindbug)
            if use_mindbug and game.game_state != GameState.GAME_OVER:
                print("Mindbug used. Current player chooses action again.")
                print_game_state(game)
                player_turn(game)
                return
        except ValueError as exc:
            print(f"Could not play card: {exc}")
    else:
        player_turn_attack(game)

    if game.game_state != GameState.GAME_OVER:
        game.end_turn()


def player_turn_attack(game: Game) -> None:
    attacker_owner = game.current_player
    defender_owner = game.opponent

    if not attacker_owner.cards_laid_out:
        print("No creatures to attack with.")
        #print_game_state(game)
        player_turn(game)
        return

    print("\nYour creatures:")
    legal_attacker_indices: list[int] = []
    for i, card in enumerate(attacker_owner.cards_laid_out):
        if card.cannot_attack:
            continue
        legal_attacker_indices.append(i)
        print(f"  [{i}] {card.short_label()}")

    if len(legal_attacker_indices) == 0:
        print("No creatures can attack right now.")
        player_turn(game)
        return

    while True:
        raw_attacker = input("Choose attacker index: ").strip()
        if not raw_attacker.isdigit():
            print("Please enter a number.")
            continue
        attacker_idx = int(raw_attacker)
        if attacker_idx in legal_attacker_indices:
            break
        print("Choose one of the listed attacker indices.")

    attacker = attacker_owner.cards_laid_out[attacker_idx]

    if not defender_owner.cards_laid_out:
        try:
            game.attack(attacker_idx, None)
        except ValueError as exc:
            print(f"Could not attack: {exc}")
        return

    if CardSpecialType.HUNTER in attacker.special_types:
        print("\nAttacker chooses target creature (HUNTER):")
        hunter_target_indices = game.get_eligible_defender_indices(
            attacker_idx, hunter_target_override=True
        )
        for i in hunter_target_indices:
            print(f"  [{i}] {defender_owner.cards_laid_out[i].short_label()}")
        print("  [s] Skip target selection")
        hunter_choice = input(
            f"{attacker_owner.name}, choose target index or s: "
        ).strip().lower()

        if hunter_choice != "s":
            try:
                if not hunter_choice.isdigit():
                    raise ValueError("Target index must be a number or s.")
                defender_idx = int(hunter_choice)
                if defender_idx not in hunter_target_indices:
                    raise ValueError("Choose one of the listed target indices or s.")
                game.attack(
                    attacker_idx,
                    defender_idx,
                    hunter_target_override=True,
                )
            except ValueError as exc:
                print(f"Could not attack: {exc}")
            return

    print("\nOpponent chooses from eligible blockers:")
    print("  [x] Let attack go through (direct life damage)")
    legal_defender_indices = game.get_eligible_defender_indices(
        attacker_idx, hunter_target_override=False
    )
    for i in legal_defender_indices:
        print(f"  [{i}] {defender_owner.cards_laid_out[i].short_label()}")

    if len(legal_defender_indices) == 0:
        print("No legal blockers. Attack goes directly.")
        try:
            game.attack(attacker_idx, None, hunter_target_override=False)
        except ValueError as exc:
            print(f"Could not attack: {exc}")
        return

    target = input(f"{defender_owner.name}, choose defender index or x: ").strip().lower()

    try:
        if target == "x":
            game.attack(attacker_idx, None, hunter_target_override=False)
        else:
            if not target.isdigit():
                raise ValueError("Defender index must be a number or x.")
            defender_idx = int(target)
            if defender_idx not in legal_defender_indices:
                raise ValueError("Choose one of the listed defender indices or x.")
            game.attack(attacker_idx, defender_idx, hunter_target_override=False)
    except ValueError as exc:
        print(f"Could not attack: {exc}")


def main() -> None:
    print("Mindbug - Python Prototype")
    p1 = input("Player 1 name: ").strip() or "Player 1"
    p2 = input("Player 2 name: ").strip() or "Player 2"

    game = Game(
        [p1, p2],
        starting_lives=3,
        starting_hand_size=5,
        starting_draw_pile_size=5,
        players_start_with_mindbugs=2,
        await_mindbug_response=True,
    )
    game.start_game(card_pool=get_card_pool())

    while game.game_state != GameState.GAME_OVER:
        print_game_state(game)
        player_turn(game)

    print_game_state(game)
    print(f"\nWinner: {game.winner.name}")


if __name__ == "__main__":
    main()
