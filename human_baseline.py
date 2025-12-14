
import gymnasium as gym
import pygame
import numpy as np
import ale_py
from gymnasium.wrappers import ResizeObservation

# Register ALE environments
gym.register_envs(ale_py)


import argparse

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
            
            # Create a semi-transparent overlay
            overlay = pygame.Surface((screen_width * scale, screen_height * scale))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Render Text
            white = (255, 255, 255)
            
            text_game_over = font.render("GAME OVER", True, white)
            text_score = font.render(f"Score: {total_score}", True, white)
            text_relaunch = font.render("Press 'R' to Relaunch", True, white)
            text_quit = font.render("Press 'Q' to Quit", True, white)
            
            # Centering helpers
            cx = (screen_width * scale) // 2
            cy = (screen_height * scale) // 2
            
            game_over_rect = text_game_over.get_rect(center=(cx, cy - 60))
            score_rect = text_score.get_rect(center=(cx, cy - 20))
            relaunch_rect = text_relaunch.get_rect(center=(cx, cy + 40))
            quit_rect = text_quit.get_rect(center=(cx, cy + 80))
            
            screen.blit(text_game_over, game_over_rect)
            screen.blit(text_score, score_rect)
            screen.blit(text_relaunch, relaunch_rect)
            screen.blit(text_quit, quit_rect)
            
            pygame.display.flip()
            
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting_for_input = False
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                            waiting_for_input = False
                            running = False
                        elif event.key == pygame.K_r:
                            waiting_for_input = False
                            # running stays True, so outer loop repeats

                clock.tick(10)

    pygame.quit()
    env.close()

if __name__ == "__main__":
    main()
