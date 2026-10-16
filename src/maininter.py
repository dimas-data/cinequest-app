import hashlib
import heapq
from collections import deque
from IPython.display import clear_output
import csv
import ast

def clear_console(header=""):
    """Clears the Jupyter Notebook cell output."""
    # Print a big, obvious separator
    print("\n" + "="*40)
    if header:
        print(f"  >>> {header.upper()} <<<")
    print("="*40 + "\n")

def clear_console2(header=""):
    """Clears the Jupyter Notebook cell output."""
    # Print a big, obvious separator
    print("\n" + "="*56)
    if header:
        print(f"  >>> {header.upper()} <<<")
    print("="*56 + "\n")

class UserNode:

    # Linked list nodes for each user
    def __init__(self, username, password, per_list, next_node=None):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        # password.encode() change the actual password from string to bytes
        # hashlib.sha256() make sure the password size is not over the limit 256 bits
        # .hexdigest() change the output of the formula into something admin can read 
        self.per_list = per_list  # The pointer to personal list
        self.next = next_node     # Pointer to the next user in the chain

class UserManager:
    
    def __init__(self, filename="users_data.csv"):
        self.head = None          # Owner of linked list above
        self.username_hash = {}   # Your Hash Table for O(1) duplicate checks
        self.filename = filename
        self.global_movie_counts = {}
        self.load_from_csv()

    def save_to_csv(self):
        """Saves all users from the Hash Table to a CSV file."""
        with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Header: Username, PasswordHash, PersonalList
            writer.writerow(["username", "password_hash", "per_list"])
            
            for username, node in self.username_hash.items():
                # We save the list as a string
                writer.writerow([node.username, node.password_hash, str(node.per_list)])

    def load_from_csv(self):
        """Rebuilds the linked list and hash table from the CSV file."""
        try:
            with open(self.filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    username = row['username']
                    pwd_hash = row['password_hash']
                    # ast.literal_eval converts "[[ 'Movie', 1 ]]" back to a real list
                    per_list = ast.literal_eval(row['per_list'])
                    # Inside load_from_csv, after you get the per_list:
                    for movie_name, count in per_list:
                        self.global_movie_counts[movie_name] = self.global_movie_counts.get(movie_name, 0) + count
                    
                    # Create the node and rebuild the structure
                    new_node = UserNode(username, "dummy", per_list, self.head)
                    new_node.password_hash = pwd_hash # Restore the actual hash
                    self.head = new_node
                    self.username_hash[username] = new_node
        except FileNotFoundError:
            # If no file exists yet, just start fresh
            pass
    
    def register(self):
        clear_console("     CREATE NEW ACCOUNT    ")
        username = input("Choose a username: ").strip() # .strip() clean spaces at the start and end

        # Use the Hash Table (Dictionary) for instant checking
        if username in self.username_hash:
            print(f"Username '{username}' already taken! Please choose a different username.\n")
            return

        password = input("Choose a password: ").strip()
        
        # Create the Node and link it
        # We put the new node at the front (Head) of the list
        new_node = UserNode(username, password, [], self.head)
        self.head = new_node

        # Update the Hash Table so this name is now "reserved"
        self.username_hash[username] = new_node # username is key, new_node is the value
        self.save_to_csv()
        
        print(f"Account created for {username}\n")
        return

    def login(self):
        clear_console("        LOGIN SYSTEM        ")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        input_hash = hashlib.sha256(password.encode()).hexdigest()

        # Instant lookup using our Hash Table
        user = self.username_hash.get(username)

        # if user exists and password the same as in the hash table
        if user and user.password_hash == input_hash: 
            print(f"Welcome back, {user.username}")
            return user
        
        print("Invalid username or password.")
        return None

    def delete_account(self, username):
    # 1. Check if the user exists in the Hash Table
        if username in self.username_hash:
            confirm = input(f"Are you sure you want to delete account '{username}'? (yes/no): ").lower()
            if confirm == 'yes':
                # 2. Remove from the Hash Table
                del self.username_hash[username]
            
                # 3. Optional: If you are using the Linked List (head), 
                # you'd need to re-link it, but for a 2-day deadline, 
                # the Hash Table is what matters for the CSV!
            
                # 4. Save the new state to CSV
                self.save_to_csv()
                print(f"Account '{username}' has been deleted.")
                return True
        else:
            print("User not found.")
        return False
    
    def manage_personal_list(self, active_user, df_prep):
        while True:   
            clear_console2(f"      {active_user.username.upper()}'S PERSONAL MOVIE LIST      ")
            print("--------------------------------------------------")
            
            # 1. VIEW: Always display current list
            if not active_user.per_list:
                print("Your list is currently empty.")
            else:
                for i, movie in enumerate(active_user.per_list, 1):
                    print(f"{i}. {movie[0]}")
            
            print("--------------------------------------------------")
            print("Options: Add - Add New | Delete - Delete Movie | Back - Back to Menu | Recommend - Trending Movies")
            choice = input("Choose an option: ").strip().lower()

            if choice == 'add':
                # Redirects to the browsing/adding function we already built
                # Once the user "Quits" browsing, they land back here automatically
                self.display_movies(df_prep, active_user)

            elif choice == 'delete':
                if not active_user.per_list:
                    print("\nNothing to delete!")
                    input("Press Enter to continue...")
                    continue
                
                # DELETE logic: using numbers is cleaner than typing names
                try:
                    idx = int(input("\nEnter the number of the movie to remove: "))
                    if 1 <= idx <= len(active_user.per_list):
                        removed = active_user.per_list.pop(idx - 1)
                        self.save_to_csv()
                        print(f"Removed '{removed}' from your list.")
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Please enter a valid number.")
                    input("\nPress Enter to refresh...")

            elif choice == 'recommend':
                trend.formula(self.global_movie_counts)
                trend.display_top10()
            
            elif choice == 'back':
                break # Returns to the Main User Menu

            else:
                print("\n[!] Invalid option. Please type 'Add', 'Delete', or 'Back'.")
                input("Press Enter to try again...")
        return

    def display_movies(self, df_prep, active_user):
        start_row = 0
        page_size = 50
        total_movies = len(df_prep)

        while True:
            # Slice the dataframe for the current page
            end_row = start_row + page_size
            current_page_df = df_prep.iloc[start_row:end_row]

            clear_console2(f" AVAILABLE MOVIES (Showing {start_row + 1} to {min(end_row, total_movies)} of {total_movies}) ")
            print("--------------------------------------------------")
            print(current_page_df[['name', 'genre']].to_string(index = True))
            print("--------------------------------------------------")

            print("\nOptions: Next - Next Page | Previous - Previous Page | Add - Add Movie | Quit - Quit to Menu")
            choice = input("Choose an option: ").strip().lower()

            if choice == 'next':
                if end_row < total_movies:
                    start_row += page_size
                else:
                    print("--- You are at the end of the list! ---")

            elif choice == 'previous':
                if start_row > 0:
                    start_row -= page_size
                else:
                    print("--- You are at the beginning! ---")

            elif choice == 'add':
                try:
                    # The user types the index number they see on the screen
                    index = int(input("Enter the Index number to add: "))
                    self.add_movie(active_user, df_prep, index)
                except:
                    print("Invalid input.")

            elif choice == 'quit':
                break # Exit this display loop and go back to user menu

            else:
                print("Invalid choice.")
        return

    def add_movie(self, user, df_prep, index):
        try:
            # We use .iloc as you requested (row position)
            movie_title = df_prep.iloc[index]['name']
            
            # Check if the movie is already anywhere in the list
            found = False
            for movie_item in user.per_list:
                if movie_item[0] == movie_title:
                    movie_item[1] += 1  # Found it! Just increase the count
                    found = True
                    break
            
            # If we didn't find it, we APPEND a new mini-list
            if not found:
                user.per_list.append([movie_title, 1]) # [Name, Count
                self.global_movie_counts[movie_title] = self.global_movie_counts.get(movie_title, 0) + 1
                self.save_to_csv()
                print(f"Added '{movie_title}' to your list!")
                
        except Exception as e:
            print(f"Invalid Index number. (Error: {e})")
        return

class MovieSearch:
    
    def __init__(self):
        self.table = {}
        
    def insert(self, movie_name, genre, index):
        key = movie_name.lower().strip()
        if key not in self.table:
            self.table[key] = []
        self.table[key].append({
            "name": movie_name,
            "genre": genre,
            "index": index
        })
        return
    #search function
    def search_movie(self, query):
        query = query.lower().strip()
        results = []

        # 1. Exact match check
        if query in self.table:
            results.extend(self.table[query])
        
        # 2. Keyword check if no exact match (or to be thorough)
        else:
            print(f"Checking keywords for '{query}'...")
            for key, movies in self.table.items():
                if query in key:
                    results.extend(movies)
        
        # 3. Display and Return
        if not results:
            print("No movies found.")
            return None
            
        for i, movie in enumerate(results, 1):
            print(f"{i}. [Index: {movie['index']}] {movie['name']} | Genre: {movie['genre']}")
            
        return results # Returning the list lets the user pick one to add!

#CATERGORIZATION BY GENRE
class CategoryByGenre:
    
    def __init__(self, df_prep):
        self.df_prep = df_prep
        self.genre_dict = {}

    def movie_genre(self):
        for i in range(len(self.df_prep)):
            genre = self.df_prep['genre'][i]
            movie_name = self.df_prep['name'][i]

            if genre not in self.genre_dict:
                self.genre_dict[genre] = []

            self.genre_dict[genre].append((movie_name, i))

        return self.genre_dict

    #search movies by genre
    def search_by_genre(self, genre_dict, search_genre):
        search_genre = search_genre.lower()
        matched_movies = []

        for genre, movies in genre_dict.items():
            if search_genre in genre.lower():
                matched_movies.extend(movies)
            else:
                None
        return matched_movies

class Recommendation:
    
    def __init__(self):
        # We use a deque to store the final Top 10 results
        self.top_10 = deque()

    def formula(self, global_counts):
        # 1. Clear previous recommendations
        self.top_10.clear()
        
        # 2. Build the Max Heap
        # We store (-count, movie_name)
        heap = []
        for movie_item in global_counts.items():
            name = movie_item[0]
            count = movie_item[1]
            # Push to heap: priority is -count
            heapq.heappush(heap, (-count, name))
        
        for _ in range(10):
            if heap:
                neg_count, movie_name = heapq.heappop(heap)
                # Convert count back to positive for display
                self.top_10.append((movie_name, -neg_count))
            else:
                break # Stop if there are fewer than 10 movies
        return

    def display_top10(self):
        clear_console("   TOP 10 RECOMMENDATIONS   ")
        print("----------------------------------------------")
        if not self.top_10:
            print("Not enough data. Add more movies to your list!")
        else:
            for i, (name, count) in enumerate(self.top_10, 1):
                print(f"{i}. {name} (Added by: {count} people(s))")
        print("----------------------------------------------")
        return

manager = UserManager()
#create hash table
movie_search = MovieSearch()
for index, row in df_prep.iterrows():
    movie_search.insert(row["name"].lower().strip(), row["genre"], index)
#USE THE CLASS FUNCTION
category = CategoryByGenre(df_prep)
genre_dict = category.movie_genre()
trend = Recommendation() 

while True:
    # 1. Main Login/Register Screen
    clear_console(" Cinequest - Movie Catalog  ")
    print("1 -> Register")
    print("2 -> Login")
    print("3 -> Exit System")
    main_choice = input("Select: ").strip()

    if main_choice == "1":
        manager.register()
        
    elif main_choice == "2":
        active_user = manager.login()
        
        if active_user:
            while True:
                clear_console(f"      Welcome, {active_user.username}      ")
                print("1 -> Manage My Personal List (View/Add/Delete)")
                print("2 -> Display movies")
                print("3 -> Search specific movies")
                print("4 -> Logout")
                print("5 -> Delete account")
                user_choice = input("Select: ").strip()
                
                if user_choice == "1":
                    # One call does it all!
                    manager.manage_personal_list(active_user, df_prep)
                
                elif user_choice == "2":
                    manager.display_movies(df_prep, active_user)

                elif user_choice == "3":
                    clear_console("        SEARCH MOVIES       ")
                    print("1 -> Search by genre")
                    print("2 -> Search by name")
                    search_choice = input("Select: ").strip()
                    
                    if search_choice == '1':
                        clear_console("       SEARCH BY GENRE      ")
                        #What genre we have
                        print("\nGenres available: ")
                        count = 1
                        for genre in genre_dict.keys():
                            print(f"{count}. {genre}")
                            count += 1

                        #Call the search function
                        user_input = input('Enter genre to search: ')
                        movies = category.search_by_genre(genre_dict, user_input)
                        count = 1
                        if movies:
                            print(f"\nMovies in genre {user_input}:")
                            for movie_name, movie_index in movies:
                                print(f" - [Index: {movie_index}] {movie_name}")
                            count += 1
                        else:
                            print('Genre not found.')
                        
                    elif search_choice == '2':
                        clear_console("       SEARCH BY NAME       ")
                        user_query = input("Enter the movie name: ").strip()
                        movie_search.search_movie(user_query)
                        
                elif user_choice == "4":
                    break

                elif user_choice == "5":
                    if manager.delete_account(active_user.username):
                        break
    
    elif main_choice == "3":
        print("Goodbye!")
        break # Ends the entire program
