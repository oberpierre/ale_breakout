
import gymnasium as gym
import pygame
import numpy as np
import ale_py
from gymnasium.wrappers import ResizeObservation

# Register ALE environments
gym.register_envs(ale_py)

def main():
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Atari Breakout - Human Baseline")
    
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
    
    total_score = 0.0
    step_counter = 0
    max_steps = 1000
    counting_started = False
    
    running = True
    current_action = 0 # NOOP
    
    # Reset environment initially
    env.reset()
    
    print(f"Game Ready. Press SPACE (FIRE) to start the 1000 step counter.")
    print(f"Goal: Maximize score in 1000 steps.")
    
    while running:
        # 1. Event Handling
        keys = pygame.key.get_pressed()
        action = 0 # NOOP
        
        # Check specific key presses
        if keys[pygame.K_SPACE]:
            action = 1 # FIRE
        elif keys[pygame.K_RIGHT]:
            action = 2 # RIGHT
        elif keys[pygame.K_LEFT]:
            action = 3 # LEFT
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
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
        
        # 5. Check Termination of 1000 steps
        if counting_started and step_counter >= max_steps:
             print(f"\nTime's up! Reached {max_steps} steps.")
             print(f"FINAL SCORE: {total_score}")
             running = False
             
        # 6. Handle Episode End
        if terminated or truncated:
            # Auto-reset to keep playing if within 1000 steps
            env.reset()
            
        # 7. FPS Sync
        clock.tick(60)
        
        # Optional debug print
        if counting_started and step_counter % 100 == 0:
            print(f"Step: {step_counter}/{max_steps} | Score: {total_score}")

    pygame.quit()
    env.close()

if __name__ == "__main__":
    main()
