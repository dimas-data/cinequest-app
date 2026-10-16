# Generated from: moviecatalog.ipynb
# Converted at: 2025-12-22T08:51:59.699Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import pandas as pd
filename = "movies_updated.csv"
df = pd.read_csv(filename, encoding = "utf8") # Load dataset with UTF-8 to manage modern language
rows = df.index
print("--- Movie Dataset ---")
print(f"The columns are: {df.columns.tolist()}") # Checking the columns and rows of the preprocessed dataset
print(f"There are {len(rows)} rows \n") 
print(df.head(3))
missing = df.isnull().sum()
print(f"\nMissing data based on columns are \n{missing}")
# Drop columns which isn't suitable for our project
df_prep = df.drop(columns = ["score", "rating", "year", "released", "votes", "director", "writer", "star", "country", "budget", "gross", "company", "runtime"] , axis = 1)
print("\n--- Cleaned Movie Dataset ---")
print(f"Rows and Columns: {df_prep.shape}") # Checking the columns and rows of the processed dataset
print(f"The new columns are: {df_prep.columns.tolist()}")
print(f"\n{df_prep.head(3)}")

# Checking duplicates based on the columns name and genre only
duplicate_rows1 = df_prep[df_prep.duplicated(subset=['name', 'genre'], keep=False)][['name', 'genre']]
print(f"Duplicates by name and genre:\n {duplicate_rows1.sort_values(by='name')}\n")
# Checking duplicates by adding another column to the filter, year to determine whether the data really is a duplicate
duplicate_rows2 = df[df.duplicated(subset=['name', 'genre', 'year'], keep=False)][['name', 'genre', 'year']]
print(f"Duplicates by name, genre and year:\n {duplicate_rows2.sort_values(by='name')}")
# Processed dataset is called df_prep