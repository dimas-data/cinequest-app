# Generated from: DSAPROJECTUSERLOGIIN (1).ipynb
# Converted at: 2025-12-25T22:59:42.162Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import hashlib
import pandas as pd

# --- USER MANAGER ---
class UserManager:
    class UserNode:
        def __init__(self, u, p, n, e, next_node):
            self.username = u
            self.password_hash = hashlib.sha256(p.encode()).hexdigest()
            self.name = n
            self.email = e
            self.next = next_node
            self.movies = []

    def __init__(self):
        self.head = None

    # --- REGISTER ---
    def register_user(self):
        username = input("Choose a username: ").strip()
        current = self.head
        while current:
            if current.username == username:
                print(f"Username '{username}' already taken!")
                return
            current = current.next
        password = input("Choose a password: ").strip()
        name = input("Enter your full name: ").strip()
        email = input("Enter your email: ").strip()
        self.head = self.UserNode(username, password, name, email, self.head)
        print(f"Account created for {username}!")

    # --- LOGIN ---
    def login(self):
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        current = self.head
        while current:
            if current.username == username:
                if current.password_hash == input_hash:
                    print(f"\nLOGIN SUCCESSFUL! Welcome back, {current.name}")
                    return current
                else:
                    print("Incorrect password!")
                    return None
            current = current.next
        print("User not found!")
        return None

    # --- PERSONAL LIST MOVIE ---
    def personal_list_movie(self, user):
        while True:
            print(f"\n--- 🎞️ {user.username}'s Personal Movie List ---")
            if user.movies:
                for idx, m in enumerate(user.movies, 1):
                    print(f"{idx}. {m['title']} ({m['genre']})")
            else:
                print("No movies added yet")

            print("\nOptions:")
            print("1. Add a new movie from dataset")
            print("2. Delete a movie from personal list")
            print("3. Back to Dashboard")
            choice = input("Select (1-3): ").strip()

            if choice == "1":
                self.add_movie_from_dataset(user)
            elif choice == "2":
                if not user.movies:
                    print("No movies to delete")
                    continue
                try:
                    del_idx = int(input("Enter the number of the movie to delete: ").strip())
                    if 1 <= del_idx <= len(user.movies):
                        removed = user.movies.pop(del_idx - 1)
                        print(f"'{removed['title']}' removed from your personal list.")
                    else:
                        print("Invalid number!")
                except ValueError:
                    print("Enter a valid number!")
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please select 1-3")

    # --- ADD MOVIE FROM CLEANED DATASET ---
    def add_movie_from_dataset(self, user):
        if not MOVIE_DATASET:
            print("Movie dataset not loaded.")
            return

        page_size = 20
        total_movies = len(MOVIE_DATASET)
        page = 0

        while True:
            start = page * page_size
            end = start + page_size
            if start >= total_movies:
                print("No more movies to display.")
                break

            print(f"\n--- Movies {start+1} to {min(end, total_movies)} of {total_movies} ---")
            for idx, movie in enumerate(MOVIE_DATASET[start:end], start=1):
                print(f"{idx}. {movie['name']} ({movie['genre']})")

            print("\nOptions: n=Next page, p=Previous page, q=Quit, number=Add movie")
            choice = input("Your choice: ").strip().lower()

            if choice == "n":
                if end >= total_movies:
                    print("Already on last page")
                else:
                    page += 1
            elif choice == "p":
                if page == 0:
                    print("Already on first page")
                else:
                    page -= 1
            elif choice == "q":
                break
            else:
                try:
                    num = int(choice)
                    if 1 <= num <= min(page_size, total_movies - start):
                        movie_sel = MOVIE_DATASET[start + num - 1]
                        if any(m['title'] == movie_sel['name'] for m in user.movies):
                            print(f"'{movie_sel['name']}' already in your list.")
                        else:
                            user.movies.append({"title": movie_sel['name'], "genre": movie_sel['genre']})
                            print(f"'{movie_sel['name']}' added to your personal list!")
                    else:
                        print("Invalid number!")
                except ValueError:
                    print("Enter valid number or command")

    # --- SEARCH GENRE ---
    def search_genre(self):
        genre = input("Enter genre: ").strip().lower()
        found = False
        current = self.head
        print(f"\n--- Movies in Genre '{genre}' ---")
        while current:
            for m in current.movies:
                if m['genre'].lower() == genre:
                    print(f"{m['title']} (User: {current.username})")
                    found = True
            current = current.next
        if not found:
            print("No movies found in this genre!")

    # --- SEARCH NAME ---
    def search_movie_name(self):
        name = input("Enter movie name: ").strip().lower()
        found = False
        current = self.head
        print(f"\n--- Search Results for '{name}' ---")
        while current:
            for m in current.movies:
                if name in m['title'].lower():
                    print(f"{m['title']} ({m['genre']}, User: {current.username})")
                    found = True
            current = current.next
        if not found:
            print("No movies found with that name!")
