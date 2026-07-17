import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO

def download_github_profile(username):
    """Download GitHub profile image"""
    url = f"https://github.com/{username}.png"
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return np.array(img)

def create_particle_image(image_path=None, username='vamsi80', particle_size=5, num_particles_percentage=30):
    """
    Create a particle/dots recreation of an image
    
    Parameters:
    - image_path: Path to local image (if None, downloads GitHub profile)
    - username: GitHub username (used if image_path is None)
    - particle_size: Size of particles (in pixels)
    - num_particles_percentage: Percentage of particles to use (0-100)
    """
    
    # Load image
    if image_path is None:
        print(f"Downloading GitHub profile image for @{username}...")
        img = download_github_profile(username)
    else:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from {image_path}")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    original_height, original_width = img.shape[:2]
    print(f"Original image size: {original_width}x{original_height}")
    
    # Resize for processing
    scale_factor = 800 / max(original_width, original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    img_resized = cv2.resize(img, (new_width, new_height))
    
    # Convert to grayscale for brightness calculation
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    
    # Create output canvas
    canvas = np.zeros_like(img_resized)
    
    # Calculate grid
    grid_size = particle_size
    particles = []
    
    # Generate particles based on brightness
    for y in range(0, new_height, grid_size):
        for x in range(0, new_width, grid_size):
            # Get average brightness in this region
            brightness = np.mean(gray[y:y+grid_size, x:x+grid_size])
            
            # Probability of particle based on brightness (darker = more particles)
            probability = (255 - brightness) / 255.0
            
            # Random selection based on percentage
            if np.random.random() < probability * (num_particles_percentage / 100):
                # Get the dominant color in this region
                region = img_resized[y:y+grid_size, x:x+grid_size]
                avg_color = np.mean(region, axis=(0, 1)).astype(int)
                
                particles.append({
                    'x': x,
                    'y': y,
                    'color': tuple(avg_color),
                    'size': particle_size,
                    'brightness': brightness
                })
    
    # Create particle image
    particle_image = np.zeros_like(img_resized)
    
    for particle in particles:
        x, y = particle['x'], particle['y']
        size = particle['size']
        color = particle['color']
        
        # Draw circle (particle/dot)
        cv2.circle(particle_image, (x + size//2, y + size//2), size//2, color, -1)
    
    # Create white dots version
    white_particle_image = np.zeros_like(img_resized)
    for particle in particles:
        x, y = particle['x'], particle['y']
        size = particle['size']
        cv2.circle(white_particle_image, (x + size//2, y + size//2), size//2, (255, 255, 255), -1)
    
    # Create animated transition version (if needed)
    print(f"Generated {len(particles)} particles")
    
    # Save outputs
    output_dir = "particle_images"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert back to BGR for OpenCV
    particle_image_bgr = cv2.cvtColor(particle_image, cv2.COLOR_RGB2BGR)
    white_particle_image_bgr = cv2.cvtColor(white_particle_image, cv2.COLOR_RGB2BGR)
    img_resized_bgr = cv2.cvtColor(img_resized, cv2.COLOR_RGB2BGR)
    
    # Save images
    cv2.imwrite(f"{output_dir}/01_original.jpg", img_resized_bgr)
    cv2.imwrite(f"{output_dir}/02_particle_colored.jpg", particle_image_bgr)
    cv2.imwrite(f"{output_dir}/03_particle_white.jpg", white_particle_image_bgr)
    
    # Create side-by-side comparison
    comparison = np.hstack([img_resized_bgr, white_particle_image_bgr])
    cv2.imwrite(f"{output_dir}/04_comparison.jpg", comparison)
    
    print(f"\n✅ Images saved to '{output_dir}/' directory:")
    print(f"   - 01_original.jpg (Original image)")
    print(f"   - 02_particle_colored.jpg (Colored particles)")
    print(f"   - 03_particle_white.jpg (White particles)")
    print(f"   - 04_comparison.jpg (Before & After)")
    
    return particle_image, white_particle_image, particles

def create_animated_reveal(image_path=None, username='vamsi80', particle_size=5, frames=60):
    """
    Create animated video showing particles revealing the image
    """
    import cv2
    
    # Load image
    if image_path is None:
        print(f"Downloading GitHub profile image for @{username}...")
        img = download_github_profile(username)
    else:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from {image_path}")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    original_height, original_width = img.shape[:2]
    
    # Resize for processing
    scale_factor = 800 / max(original_width, original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    img_resized = cv2.resize(img, (new_width, new_height))
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    
    # Calculate grid
    grid_size = particle_size
    particles = []
    
    # Generate all particles
    for y in range(0, new_height, grid_size):
        for x in range(0, new_width, grid_size):
            brightness = np.mean(gray[y:y+grid_size, x:x+grid_size])
            probability = (255 - brightness) / 255.0
            
            if np.random.random() < probability:
                region = img_resized[y:y+grid_size, x:x+grid_size]
                avg_color = np.mean(region, axis=(0, 1)).astype(int)
                
                particles.append({
                    'x': x,
                    'y': y,
                    'color': tuple(avg_color),
                    'size': particle_size,
                    'brightness': brightness,
                    'order': np.random.random()  # Random reveal order
                })
    
    # Sort particles by reveal order
    particles.sort(key=lambda p: p['order'])
    
    # Create video
    output_dir = "particle_images"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    video_path = f"{output_dir}/particle_reveal_animation.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (new_width, new_height))
    
    print(f"Creating animation with {len(particles)} particles...")
    
    # Create frames
    particles_per_frame = len(particles) // frames
    
    for frame_idx in range(frames):
        canvas = np.zeros((new_height, new_width, 3), dtype=np.uint8)
        
        # Draw particles up to current frame
        num_particles = min((frame_idx + 1) * particles_per_frame, len(particles))
        
        for i in range(num_particles):
            particle = particles[i]
            x, y = particle['x'], particle['y']
            size = particle['size']
            color = particle['color']
            
            # Convert RGB to BGR for OpenCV
            color_bgr = (int(color[2]), int(color[1]), int(color[0]))
            cv2.circle(canvas, (x + size//2, y + size//2), size//2, color_bgr, -1)
        
        # Add progress text
        progress = int((num_particles / len(particles)) * 100)
        cv2.putText(canvas, f"Revealing... {progress}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(canvas)
    
    out.release()
    print(f"✅ Animation saved to '{video_path}'")

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("GITHUB PROFILE PARTICLE IMAGE GENERATOR")
    print("=" * 60)
    
    # Option 1: Create static particle images
    print("\n🎨 Creating particle images from GitHub profile...")
    create_particle_image(
        username='vamsi80',
        particle_size=8,
        num_particles_percentage=40
    )
    
    # Option 2: Create animated reveal (uncomment to use)
    print("\n🎬 Creating animated reveal video...")
    create_animated_reveal(
        username='vamsi80',
        particle_size=8,
        frames=90
    )
    
    print("\n" + "=" * 60)
    print("✨ Done! Check the 'particle_images' folder for results")
    print("=" * 60)
