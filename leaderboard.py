import csv
import os
from datetime import datetime

SCORES_DIR = "scores"
LEADERBOARD_FILE = os.path.join(SCORES_DIR, "leaderboard.csv")

def save_score(name, score, steps):
    if not os.path.exists(SCORES_DIR):
        os.makedirs(SCORES_DIR)
        
    file_exists = os.path.exists(LEADERBOARD_FILE)
    
    with open(LEADERBOARD_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Score", "Steps"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, name, score, steps])
        print(f"Score saved for {name}: {score}")

def get_leaderboard_stats(target_score=None):
    if not os.path.exists(LEADERBOARD_FILE):
        return 0.0, [], None
        
    scores = []
    try:
        with open(LEADERBOARD_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    scores.append((row["Name"], float(row["Score"])))
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading leaderboard: {e}")
        return 0.0, [], None
        
    if not scores:
        return 0.0, [], None
        
    # Calculate Average
    total_score = sum(s[1] for s in scores)
    avg_score = total_score / len(scores)
    
    # Sort for ranking and top 10
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate ranks with ties (Standard Competition Ranking 1224)
    ranked_scores = []
    current_rank = 1
    for i, (name, s) in enumerate(scores):
        if i > 0 and s < scores[i-1][1]:
            current_rank = i + 1
        ranked_scores.append((current_rank, name, s))
        
    top_10 = ranked_scores[:10]
    
    player_rank = None
    if target_score is not None:
        # Find the rank for this score
        for r, n, s in ranked_scores:
            if s == target_score:
                player_rank = r
                break
    
    return avg_score, top_10, player_rank
