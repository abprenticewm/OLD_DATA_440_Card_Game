from data_gen import generate_decks
import scoring  # import whole module, not specific function


def augment_data():
    """
    Generate new decks and then run scoring once on all new data.
    """
    try:
        n = int(input("How many new decks would you like to generate? "))
        if n <= 0:
            print("Please enter a positive number.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    # Generate decks
    generate_decks(n)
    print("Deck generation completed.")

    # Run scoring once overall
    scoring.main()
    print("Scoring completed.")


if __name__ == "__main__":
    augment_data()
