# Generated from: toprecom.ipynb
# Converted at: 2025-12-27T09:52:20.233Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

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