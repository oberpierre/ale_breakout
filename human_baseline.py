
import gymnasium as gym
import pygame
import numpy as np
import ale_py
from gymnasium.wrappers import ResizeObservation

# Register ALE environments
gym.register_envs(ale_py)


import argparse
import leaderboard

def main():
    parser = argparse.ArgumentParser(description="Human Baseline for Atari Breakout")
    parser.add_argument("--steps", type=int, default=-1, help="Max steps to play (default: -1 for infinite)")
    args = parser.parse_args()

    max_steps = args.steps

    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Atari Breakout - Human Baseline")
    
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    
    # Initialize Environment
    # render_mode="rgb_array" is used because we will manually blit to pygame surface
    env = gym.make("ALE/Breakout-v5", render_mode="rgb_array", frameskip=1, repeat_action_probability=0.0)
    
    # Action mapping for Breakout
    # 0: NOOP, 1: FIRE, 2: RIGHT, 3: LEFT
    
    # Get screen dimensions from env
    obs, _ = env.reset()
    screen_height, screen_width, _ = obs.shape
    
    # Create Pygame window (scale up 3x for visibility)
    scale = 3
    screen = pygame.display.set_mode((screen_width * scale, screen_height * scale))
    clock = pygame.time.Clock()
    
    running = True
    
    while running:
        # --- Episode Setup ---
        total_score = 0.0
        step_counter = 0
        counting_started = False
        current_action = 0 # NOOP
        
        # Reset environment initially
        env.reset()
        
        if max_steps > 0:
            print(f"Game Ready. Press SPACE (FIRE) to start the {max_steps} step counter.")
            print(f"Goal: Maximize score in {max_steps} steps.")
        else:
            print(f"Game Ready. Free Play Mode (Infinite Steps). Press SPACE to play.")
            
        episode_running = True
        episode_ended_reason = None # "steps", "game_over", "quit"

        while episode_running:
            # 1. Event Handling
            keys = pygame.key.get_pressed()
            action = 0 # NOOP
            
            # Check specific key presses
            if keys[pygame.K_SPACE]:
                action = 1 # FIRE
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                action = 2 # RIGHT
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                action = 3 # LEFT
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    episode_running = False
                    running = False
                    episode_ended_reason = "quit"
            
            if not running:
                break
            
            # 2. Game Logic & Start Condition
            if not counting_started:
                if action == 1: # FIRE
                    counting_started = True
                    print(">>> COUNTER STARTED! <<<")

            # 3. Environment Step
            obs, reward, terminated, truncated, info = env.step(action)
            
            if counting_started:
                step_counter += 1
                total_score += reward
            
            # 4. Rendering
            frame = np.transpose(obs, (1, 0, 2))
            surf = pygame.surfarray.make_surface(frame)
            
            # Scale to window
            surf = pygame.transform.scale(surf, (screen_width * scale, screen_height * scale))
            
            screen.blit(surf, (0, 0))
            pygame.display.flip()
            
            # 5. Check Termination of steps (if limit set)
            if max_steps > 0 and counting_started and step_counter >= max_steps:
                 print(f"\nTime's up! Reached {max_steps} steps.")
                 print(f"FINAL SCORE: {total_score}")
                 episode_running = False
                 episode_ended_reason = "steps"
                 
            # 6. Handle Episode End
            if terminated or truncated:
                episode_running = False
                episode_ended_reason = "game_over"
                
            # 7. FPS Sync
            clock.tick(60)
            
            # Optional debug print
            if counting_started and step_counter % 100 == 0:
                if max_steps > 0:
                    print(f"Step: {step_counter}/{max_steps} | Score: {total_score}")
                else:
                    print(f"Step: {step_counter} | Score: {total_score}")

        # --- Game Over Screen Loop ---
        if running: # Only show if we didn't just quit
            print("Displaying Game Over Screen...")
            waiting_for_input = True
            
            # Game Over State
            name_submitted = False
            player_name = ""
            
            # Fetch baseline once
            # Note: We pass total_score to find our rank. 
            # Limitation: If multiple people have duplicate scores, this returns rank of first match.
            current_baseline, top_10_scores, player_rank = leaderboard.get_leaderboard_stats(total_score if name_submitted else None)
            
            while waiting_for_input:
                # 1. Clear Screen & Draw Overlay each frame (to handle dynamic text)
                overlay = pygame.Surface((screen_width * scale, screen_height * scale))
                # Simple approach: Fill screen black (or dark grey) for the menu
                screen.fill((20, 20, 20))
                
                # Render Text
                white = (255, 255, 255)
                green = (0, 255, 0)
                yellow = (255, 255, 0)
                gray = (150, 150, 150)
                
                cx = (screen_width * scale) // 2
                cy = (screen_height * scale) // 2
                
                # Helper for flexible number formatting
                def fmt_num(n):
                    return f"{int(n)}" if n == int(n) else f"{n:.1f}"

                if not name_submitted:
                    # Title
                    text_game_over = font.render("GAME OVER", True, white)
                    game_over_rect = text_game_over.get_rect(center=(cx, cy - 100))
                    screen.blit(text_game_over, game_over_rect)
                    
                    # Score
                    text_score = font.render(f"Your Score: {fmt_num(total_score)}", True, green)
                    score_rect = text_score.get_rect(center=(cx, cy - 60))
                    screen.blit(text_score, score_rect)

                    # --- State 1: Name Entry ---
                    prompt_text = font.render("Enter Name:", True, white)
                    prompt_rect = prompt_text.get_rect(center=(cx, cy))
                    screen.blit(prompt_text, prompt_rect)
                    
                    display_name = player_name if player_name else "???"
                    color = white if player_name else gray
                    input_text = font.render(display_name, True, color)
                    input_rect = input_text.get_rect(center=(cx, cy + 40))
                    screen.blit(input_text, input_rect)
                    
                    hint_text = font.render("Press ENTER to Submit", True, yellow)
                    hint_rect = hint_text.get_rect(center=(cx, cy + 100))
                    screen.blit(hint_text, hint_rect)
                    
                else:
                    # --- State 2: Menu ---
                    # Layout: Top (Summary), Middle (Leaderboard), Bottom (Controls)
                    
                    # 1. Summary (Top)
                    summary_y = 60
                    rank_str = f"#{player_rank} " if player_rank else ""
                    text_score = font.render(f"You: {rank_str}{player_name} - Score: {fmt_num(total_score)}", True, green)
                    score_rect = text_score.get_rect(center=(cx, summary_y))
                    screen.blit(text_score, score_rect)
                    
                    baseline_text = small_font.render(f"Average: {fmt_num(current_baseline)}", True, gray)
                    baseline_rect = baseline_text.get_rect(center=(cx, summary_y + 30))
                    screen.blit(baseline_text, baseline_rect)
                    
                    # 2. Leaderboard (Middle)
                    lb_y_start = summary_y + 80
                    lb_title = font.render("TOP 10 LEADERBOARD", True, yellow)
                    lb_rect = lb_title.get_rect(center=(cx, lb_y_start))
                    screen.blit(lb_title, lb_rect)
                    
                    for i, (rank, name, score) in enumerate(top_10_scores):
                        entry_str = f"{rank}. {name} - {fmt_num(score)}"
                        entry_text = small_font.render(entry_str, True, white)
                        entry_rect = entry_text.get_rect(center=(cx, lb_y_start + 40 + (i * 25)))
                        screen.blit(entry_text, entry_rect)
                        
                    # 3. Controls (Bottom)
                    controls_y = screen_height * scale - 60
                    relaunch_text = font.render("Press 'R' to Relaunch, 'Q' to Quit", True, white)
                    relaunch_rect = relaunch_text.get_rect(center=(cx, controls_y))
                    screen.blit(relaunch_text, relaunch_rect)

                pygame.display.flip()
                
                # Event Handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting_for_input = False
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if not name_submitted:
                            # State 1: Typing
                            if event.key == pygame.K_RETURN:
                                if not player_name.strip():
                                    player_name = "???"
                                leaderboard.save_score(player_name, total_score, step_counter)
                                name_submitted = True
                                # Refresh baseline and stats with rank
                                current_baseline, top_10_scores, player_rank = leaderboard.get_leaderboard_stats(total_score)
                            elif event.key == pygame.K_BACKSPACE:
                                player_name = player_name[:-1]
                            elif event.key == pygame.K_SPACE:
                                player_name += " "
                            else:
                                # Add alphanumeric
                                if len(player_name) < 15: # Limit length
                                    # Use unicode to catch shift/caps correctly
                                    if event.unicode.isprintable():
                                        player_name += event.unicode
                        else:
                            # State 2: Menu
                            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                                waiting_for_input = False
                                running = False
                            elif event.key == pygame.K_r:
                                waiting_for_input = False
                                # running stays True, so outer loop repeats

                clock.tick(30)

    pygame.quit()
    env.close()

if __name__ == "__main__":
    main()
