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

            self.genre_dict[genre].append(movie_name)

        return self.genre_dict

#search movies by genre
def search_by_genre(genre_dict, search_genre):
    search_genre = search_genre.lower()
    matched_movies = []

    for genre, movies in genre_dict.items():
        if search_genre in genre.lower():
            matched_movies.extend(movies)
        else:
            None
    return matched_movies

#USE THE CLASS FUNCTION
category = CategoryByGenre(df_prep)
genre_dict = category.movie_genre()

#What genre we have
print("\nGenres available: ")

count = 1
for genre in genre_dict.keys():
    print(f"{count}. {genre}")
    count += 1

#Call the search function
user_input = input('Enter genre to search: ')

movies = search_by_genre(genre_dict, user_input)

count = 1
if movies:
    print(f"\n {count}. Movies in genre {user_input}:")
    for movie in movies:
        print(" -", movie)
        count += 1
else:
    print('Genre not found.')
