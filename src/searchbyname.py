class MovieSearchHashTable:
    def __init__(self):
        self.table = {}
    def insert(self, movie_name, genre):
        key = movie_name.lower()
        if key not in self.table:
            self.table[key] = []
        self.table[key].append({
            "name": movie_name,
            "genre": genre
        })
    #search function
    def search_movie(self, query):
        query = query.lower()
        found = False
        # exact movie name search (O(1))
        if query in self.table:
            print(f"Exact match found for '{query}':")
            for movie in self.table[query]:
                print(f" - {movie['name']} | Genre: {movie['genre']}")
            print()
            return
        #keyword search (O(n))
        print(f"Searching movies with keyword '{query}':")
        for key, movies in self.table.items():
            if query in key:
                for movie in movies:
                    print(f" - {movie['name']} | Genre: {movie['genre']}")
                    found = True
        if not found:
            print("No movies found.")
        print()
#create hash table
movie_search = MovieSearchHashTable()
for _, row in df_prep.iterrows():
    movie_search.insert(row["name"], row["genre"])
print("Movie search hash table created successfully!\n")




