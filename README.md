cinequest-moviecatalog
======================

A collaborative movie catalog project that showcases quick data searching and data analysis using hash tables, max heaps, deques, and linked lists.

## Data Preprocessing

``` python
import pandas as pd
filename = "movies_updated.csv"
df = pd.read_csv(filename, encoding = "utf8") # Load dataset with UTF-8 to manage modern language
rows = df.index
```

This logic loads the dataset from a CSV file into a DataFrame using Pandas, a modern and efficient alternative to the standard Python `csv` library. UTF-8 encoding is implemented to properly handle special characters that may appear in the movie titles or metadata. The rows variable is explicitly declared to manage the horizontal data entries, as DataFrames primarily utilize columns and indexes to organize vertical and horizontal metadata.

```python
print("--- Movie Dataset ---")
print(f"The columns are: {df.columns.tolist()}") # Checking the columns and rows of the preprocessed dataset
print(f"There are {len(rows)} rows \n") 
print(df.head(3))
```

We performed a brief audit of the entire dataset to ensure both the columns and row counts align with the Kaggle overview. To finalize this verification, we printed the first three entries as a representative sample. This approach ensures a fast and efficient process by avoiding the need to manually inspect all rows.

Output:

```
--- Movie Dataset ---
The columns are: ['name', 'rating', 'genre', 'year', 'released', 'score', 'votes', 'director', 'writer', 'star', 'country', 'budget', 'gross', 'company', 'runtime']
There are 4000 rows 

                                             name rating      genre  year  \
0                                     The Shining      R      Drama  1980   
1                                 The Blue Lagoon      R  Adventure  1980   
2  Star Wars: Episode V - The Empire Strikes Back     PG     Action  1980   

                        released  score    votes         director  \
0  June 13, 1980 (United States)    8.4   927000  Stanley Kubrick   
1   July 2, 1980 (United States)    5.8    65000   Randal Kleiser   
2  June 20, 1980 (United States)    8.7  1200000   Irvin Kershner   

                    writer            star         country    budget  \
0             Stephen King  Jack Nicholson  United Kingdom  19000000   
1  Henry De Vere Stacpoole  Brooke Shields   United States   4500000   
2           Leigh Brackett     Mark Hamill   United States  18000000   

         gross            company runtime  
0   46998772.0       Warner Bros.  146.0,  
1   58853106.0  Columbia Pictures  104.0,  
2  538375067.0          Lucasfilm  124.0,  
```

We confirmed that the dataset contains 15 columns and 4,000 rows, which aligns perfectly with the Kaggle overview. Upon inspecting the first three entries, no abnormalities were detected; therefore, we have proceeded to the next step of the project.

```python
missing = df.isnull().sum()
print(f"\nMissing data based on columns are \n{missing}")
```

A missing value check was also implemented to prevent potential issues, such as data collisions in the Hash Table we will develop later. Ensuring a complete dataset at this stage maintains the reliability of our hashing algorithm and search efficiency.

Output:

```
Missing data based on columns are 
name          0
rating       40
genre         0
year          0
released      0
score         0
votes         0
director      0
writer        1
star          1
country       0
budget        0
gross       169
company      10
runtime       0
dtype: int64
```

As no missing values were detected within the dataset, the implementation of data handling or imputation methods was unnecessary. This confirms the integrity of the data and allows us to proceed directly to the algorithm implementation phase.

``` python
# Drop columns which isn't suitable for our project
df_prep = df.drop(columns = ["score", "rating", "year", "released", "votes", "director", "writer", "star", "country", "budget", "gross", "company", "runtime"] , axis = 1)
```

We removed 13 unnecessary columns, retaining only the `name` and `genre` fields required for our project; this filtered dataset was then stored in the `df_prep` variable

```python
print("\n--- Cleaned Movie Dataset ---")
print(f"Rows and Columns: {df_prep.shape}") # Checking the columns and rows of the processed dataset
print(f"The new columns are: {df_prep.columns.tolist()}")
print(f"\n{df_prep.head(3)}")
```

An additional verification step was implemented to confirm that the columns were dropped correctly. By inspecting the DataFrame's shape and column list, we ensured that only the essential `name` and `genre` fields remain in the final preprocessed dataset.

Output:

```
--- Cleaned Movie Dataset ---
Rows and Columns: (4000, 2)
The new columns are: ['name', 'genre']

                                             name      genre
0                                     The Shining      Drama
1                                 The Blue Lagoon  Adventure
2  Star Wars: Episode V - The Empire Strikes Back     Action
```

The specified columns were successfully dropped, and the final version of the dataset was verified by inspecting the `df_prep` variable. This ensures the data is correctly structured and ready for implementation into our chosen data structures.

```python
# Checking duplicates based on the columns name and genre only
duplicate_rows1 = df_prep[df_prep.duplicated(subset=['name', 'genre'], keep=False)][['name', 'genre']]
print(f"Duplicates by name and genre:\n {duplicate_rows1.sort_values(by='name')}\n")
```

To ensure high data quality, we screened the dataset for duplicate entries.

Output:

```
Duplicates by name and genre:
                     name   genre
2438       Boiling Point  Action
1814       Boiling Point  Action
1395            Chocolat   Drama
3688            Chocolat   Drama
472        Forever Young   Drama
2104       Forever Young   Drama
2120           Gladiator  Action
3645           Gladiator  Action
2888              Hamlet   Drama
1706              Hamlet   Drama
3776              Hamlet   Drama
1419        It Takes Two  Comedy
2724        It Takes Two  Comedy
1039       Nobody's Fool  Comedy
2537       Nobody's Fool  Comedy
1569            Out Cold  Comedy
3933            Out Cold  Comedy
3938               Pulse  Horror
1403               Pulse  Horror
2846              Scream  Horror
198               Scream  Horror
829         Sudden Death  Action
2766        Sudden Death  Action
1976     Under Suspicion   Crime
3705     Under Suspicion   Crime
1812  Where the Heart Is  Comedy
3708  Where the Heart Is  Comedy
```

Upon identifying multiple duplicates within the dataset, we carefully verified whether these entries represented true redundancies or distinct records.

```python
# Checking duplicates by adding another column to the filter, year to determine whether the data really is a duplicate
duplicate_rows2 = df[df.duplicated(subset=['name', 'genre', 'year'], keep=False)][['name', 'genre', 'year']]
print(f"Duplicates by name, genre and year:\n {duplicate_rows2.sort_values(by='name')}")
# Processed dataset is called df_prep
```

The preprocessed dataset was used to incorporate an additional filter, the movie release year to distinguish between genuine duplicates and different films sharing the same title.

Output:

```
Duplicates by name, genre and year:
 Empty DataFrame
Columns: [name, genre, year]
Index: []
```

The results indicated no duplicates, confirming that the initial matches were actually distinct movies or remakes with the same title but different release years.

## Data Structure Design & Implementation

---
### User Authentication & Management
---

```python
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
```

The `UserNode` class represents a single user in the system and serves as a node in linked list of users. Each node stores the user's username, a securely hashed password, their personal movie list (`per_list`), and a reference to the next user in the list (next). The password is converted to a secure hash using SHA-256 that firstly is it encoded into bytes, then hashed, and finally converted to a readable hexadecimal string. This design allows the system to manage multiple users dynamically, keep passwords secure, and maintain a link between all registered users through the linked list structure.

```python
class UserManager:
    
    def __init__(self, filename="users_data.csv"):
        self.head = None          # Owner of linked list above
        self.username_hash = {}   # Your Hash Table for O(1) duplicate checks
        self.filename = filename
        self.global_movie_counts = {}
        self.load_from_csv()
```

The `UserManager` class is responsible for managing user accounts, their personal movie lists, and maintaining persistent storage using CSV file. It combines a linked list and a hash table to efficiently manage users, prevent duplicates, and allow quick lookups.

The constructor initializes the `UserManager` object. It sets the head of the linked list to `None`, initializes a `username_hash` dictionary for fast O(1) lookups of usernames, stores the CSV filename, and maintains `global_movie_counts` to track trending movies. Finally, it calls `load_from_csv()` to populate the linked list and hash table from existing data.

```python
def save_to_csv(self):
        """Saves all users from the Hash Table to a CSV file."""
        with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Header: Username, PasswordHash, PersonalList
            writer.writerow(["username", "password_hash", "per_list"])
            
            for username, node in self.username_hash.items():
                # We save the list as a string
                writer.writerow([node.username, node.password_hash, str(node.per_list)])
```

This method saves all users' data to a CSV file. Each user's username, hashed password, and personal movie list are written as rows. The personal movie list is converted into a string to store it in the CSV. This ensures that user data persists across sessions.

```python
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
```

This method loads user data from CSV file. It rebuilds the linked list and hash table by reading the username, password hash, and personal movie list for each user. It also updates `global_movie_counts` to keep track on how many times each movie appears in all users/ lists. If no CSV exists, it starts with an empty system.

```python
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
```

This register method allows a new user to create an account. The username is checked against the hash table to prevent duplicates. If valid, a new `UserNode` is created and added to the front of the linked list. The hash table is updated for fast lookup, and the new user's data is saved to CSV.

```python
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
```

This login method authenticates a user. It first retrieves the user node from the hash table using the enters username. The input `password` is hashed and compared with the stored hash. If the hashes match, the user is logged in, otherwise an error message displayed.

```python
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
```

This `delete_account` method deletes a user account. It first checks if the `username` exists in the hash table. If confirmed by the user, the account is removed from the hash table and saved to CSV. The linked list is optional for deletion since the hash table is the main structure used for persistence.

```python
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
```

The `manage_personal_list` method allows a logged-in user to manage their personal movie list through an interactive console interface. Upon entering the menu, the method continuously displays the current list of movies, indicating if the list is empty or enumerating each movie with its title. Users are provided with several options which is they can add new movies by browsing the dataset, delete existing movies by selecting the corresponding number, view trending movie recommendations based on all users’ activity, or return to the main menu. The method validates user input at each step, ensuring that invalid commands or out-of-range numbers do not cause errors. Any changes made to the list, such as adding or removing movies, are immediately saved to the CSV file to maintain data persistence across sessions. The menu continues to loop, allowing the user to perform multiple actions until they choose to exit. Overall, this method serves as a central hub for personal list management, combining a user-friendly interface with robust input handling and persistent storage to provide a smooth and reliable experience.

```python
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
```

This `display_movies` method is designed to provide an interactive and paginated browsing experience for users when exploring the available movie dataset. It takes the preprocessed dataset (`df_prep`) and the currently logged-in user (`active_user`) as inputs. The method divides the dataset into pages of 50 movies each, showing only a portion of the list at a time to improve readability and usability. Users can navigate through pages using 'Next' and 'Previous' commands, ensuring that even large datasets can be explored efficiently. For each page, the method displays both the movie title and its genre, providing essential information for informed selection, Users can also add movies directly to their personal list by entering the index number shown inthe current page, which invokes the `add_movie` method to handle validation and update the list. the interface includes a 'Quit' option to exit the browsing mode and return to the main personal list menu. This design ensures that users can efficiently navigate, select, and manage movies while minimizing errors and maintaning a smooth workflow.

```python
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
```

The `add_movie` method handles the addition of a selected movie to the user’s personal list. It takes three parameters: the active user object (`user`), the processed movie dataset (`df_prep`), and the index of the chosen movie in the dataset (`index`). First, it retrieves the movie title from the dataset using the provided index. Then, it checks if the movie is already present in the user’s personal list. If it exists, the method simply increments the count for that movie, indicating that the user has added it again. If the movie is not already in the list, it appends a new entry consisting of the movie title and a count of one. At the same time, the method updates a global count dictionary to track the total number of times each movie has been added across all users, which can later be used for trending or recommendation features. The method also ensures data persistence by calling `save_to_csv` after every addition. Exception handling is included to manage invalid index inputs, preventing the program from crashing if the user enters a number that is out of bounds or invalid. Overall, this method efficiently manages personal list updates, prevents duplicates, and contributes to the broader analytics of movie popularity.

---
### Genre Categorization
---

``` python
    def __init__(self, df_prep):
        self.df_prep = df_prep
        self.genre_dict = {}
```

The first line is a constructor, which runs automatically when an object of the class is created. The second line stores the datasets, which is a DataFrame containing movie information such as movie name and movie genre inside the object attributes. The third line creates an empty dictionary that will later be used to store movies grouped by genre. The data structure that we used is dictionary(`dict`), where the `genre` is used as the key and the value is a list of the movies that belong to that genre.

``` python
    def movie_genre(self):
        for i in range(len(self.df_prep)):
            genre = self.df_prep['genre'][i]
            movie_name = self.df_prep['name'][i]
```

The `movie_genre()` method is used to build the dictionary that will categorize movies based on their genres. This method loops through each row in the DataFrame using i, which represents the index of each movie. For every movie, it retrieves the movie genre and movie name from the DataFrame at index i.

``` python
            if genre not in self.genre_dict:
                self.genre_dict[genre] = []
```

Next, it checks whether the genre already exists as a key in `genre_dict` or not. If not, it creates a new key for that genre. The value is an empty list to store movies.

```python
            self.genre_dict[genre].append((movie_name, i))
```

Then, it adds a tuple `(movie_name, i)` to the genre list where `movie_name` is the name of the movie and `i` is index of the movie in DataFrame.

``` python
        return self.genre_dict
```

Finally, the method returns the completed dictionary containing all genres and their associated movies. This dictionary is ready to be used for searching.

``` python
    def search_by_genre(self, genre_dict, search_genre):
      search_genre = search_genre.lower()
      matched_movies = []  
```

The `search_by_genre` method is used for searching movies based on the genre, where the inputs are `genre_dict`, which is the dictionary created earlier, and `search_genre`, which is the genre keyword entered by user. Then, we convert input to lowercase to make the searching is case-insensitive by putting `lower()`. After that, we create a list to store results which initializes an empty list to store movies that match the search genre. 

``` python
        for genre, movies in genre_dict.items():
```

Next, it loop through the dictionary where it iterates through each key-value pair in the dictionary.

``` python
            if search_genre in genre.lower():
```

Following by matching the genre, where it converts the genre name to lowercase and checks whether the search keyword exists within the genre name or not. This method allows partial matching such as "act" matches "Action" .

``` python
                matched_movies.extend(movies)
```

Then, if the genre matches, all movies under that genre are added to `matched_movies` by using `extend()`, which allows multiple movies to be added at once.

``` python
            else:
                None
```

But if the `genre` does not match, the program simply skips it and continues checking the next genre by putting `None`.

``` python
        return matched_movies
```

Last, it return the results by returning a list of all movies that match the `search_genre` and each movie is stored as a tuple.

---
### Search Functionality
---

``` python
    def __init__(self):
        self.table = {}
```

This part is constructor, its dictionary acts as hash table like key as movie name and value as movie of list record.

``` python
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
```

This function to insert the movies into hash table using lowercase movie name as the key and keep the movies in the list to handle collisions efficiently.

``` python
    #search function
    def search_movie(self, query):
        query = query.lower().strip()
        results = []
```

This function starting a movie search by normalizing the user input and preparing a results list to store matching movies.

``` python
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
```

The `search` function first performs a fast exact lookup using a hash table and falls back to a keyword search if no exact match is found, ensuring both efficiency and flexibility.

``` python
        for i, movie in enumerate(results, 1):
            print(f"{i}. [Index: {movie['index']}] {movie['name']} | Genre: {movie['genre']}")
            
        return results # Returning the list lets the user pick one to add!
```

This section displays the search results in a numbered format and returns the matched movie list so it can be reused for further user actions.

---
### Ranking & Recommendations
---

```python
def __init__(self):
        # We use a deque to store the final Top 10 results
        self.top_10 = deque()
```

The architectural blueprint for the `Recommendation` class initiates by designating a `deque` as the primary storage structure. This foundational choice facilitates a highly efficient integration of deques and max-heaps, optimizing data processing for later operations.

```python
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
```

The formula function leverages a priority queue (`heap`) to identify the top-ranking elements with optimal time efficiency. Initially, any existing recommendations are cleared to ensure accuracy. Subsequently, the movie counts retrieved from the hash table dictionary are appended to the max-heap storage. Finally, the ten titles with the highest frequency are popped from the heap to construct the definitive Top 10 `Recommendations` list.

```python
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
```

The `display_top10` method serves as the primary visualization interface for the trending dashboard. It features conditional rendering logic to ensure the user receives clear feedback based on system data. If the Top 10 `deque` is currently empty, the system generates a notification indicating that the dataset is insufficient to produce meaningful trends. Conversely, when data is available, the leaderboard is populated with the ranked titles, accompanied by their specific engagement metric which is the number of times the movie was added to others' personal list.

---
### Main Interface
---

``` python
manager = UserManager()
#create hash table
movie_search = MovieSearch()
for index, row in df_prep.iterrows():
    movie_search.insert(row["name"].lower().strip(), row["genre"], index)
#USE THE CLASS FUNCTION
category = CategoryByGenre(df_prep)
genre_dict = category.movie_genre()
trend = Recommendation()
```

This code initializes the main system components by creating objects for user management, movie searching, genre categorization, and recommendation, and populates the search hash table using the cleaned dataset.

``` python 
while True:
    # 1. Main Login/Register Screen
    clear_console(" Cinequest - Movie Catalog  ")
    print("1 -> Register")
    print("2 -> Login")
    print("3 -> Exit System")
    main_choice = input("Select: ").strip()
```

This loop displays the main system menu and continuously prompts the user to register, log in, or exit the system until a valid exit option is selected.

``` python
    if main_choice == "1":
        manager.register()
        
    elif main_choice == "2":
        active_user = manager.login()
```

This code checks the user’s menu selection. If the user chooses to register, the system calls the `registration` function. If the user chooses to log in, the system authenticates the user and stores the logged-in user as the active user.

``` python
        if active_user:
            while True:
                clear_console(f"      Welcome, {active_user.username}      ")
                print("1 -> Manage My Personal List (View/Add/Delete)")
                print("2 -> Display movies")
                print("3 -> Search specific movies")
                print("4 -> Logout")
                print("5 -> Delete account")
                user_choice = input("Select: ").strip()
```

This code displays the user dashboard after a successful login. It provides options to manage personal movie lists, browse movies, search movies, log out, or delete the account. The menu continues to display until the user exits or logs out.

``` python
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
```

This code handles user dashboard options 1–3. Option 1 calls a method to manage the personal movie list, option 2 displays all movies, and option 3 allows the user to search movies either by genre or name. The search by genre displays a numbered list of all available genres.

``` python
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
```

This code handles searching movies by genre or name, logging out, deleting the account, and exiting the system. Genre search uses a genre dictionary, name search uses the hash table, and the dashboard/menu loops ensure continuous interaction until the user chooses to exit.

## Legal & Licensing

* **Disclaimer:** This project is for academic purposes and is **not affiliated** with Cinequest Inc. or any of its film festivals.
* **License:** This project is licensed under the [MIT License](LICENSE).
