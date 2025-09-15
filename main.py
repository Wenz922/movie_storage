import movies
from colorama import Fore, Style


# global state
active_user = None

# ------------------- MENU -------------------
def menu_choice_display():
    print(Fore.GREEN + "\nMenu:")
    print("0. Exit")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie (add note)")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Movies rating by year")
    print("10. Generate website")
    print("11. Switch user" + Style.RESET_ALL)


def main():
    """ main function"""
    global active_user
    print(Fore.GREEN + Style.BRIGHT + "********** My Movies Database **********" + Style.RESET_ALL)

    movies.select_user()

    while True:
        menu_choice_display()
        menu_input = input("\nEnter choice (0-11): ")
        if menu_input == "0":
            print(Fore.GREEN + "Bye! See you next time.!" + Style.RESET_ALL)
            break
        elif menu_input == "1":
            movies.list_movies()
        elif menu_input == "2":
            movies.add_movie()
        elif menu_input == "3":
            movies.delete_movie()
        elif menu_input == "4":
            movies.update_movie()
        elif menu_input == "5":
            movies.movies_stats()
        elif menu_input == "6":
            movies.random_movie()
        elif menu_input == "7":
            movies.search_movie()
        elif menu_input == "8":
            movies.movies_sorted_by_rating()
        elif menu_input == "9":
            movies.movies_sorted_by_year()
        elif menu_input == "10":
            movies.generate_website()
        elif menu_input == "11":
            movies.select_user()
        else:
            print(Fore.RED + "Invalid Input! Try again." + Style.RESET_ALL)

        input("\nPress Enter to continue")


if __name__ == "__main__":
    main()

