import pygame
import math
import random
pygame.init()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Planet Simulation")

#MUSIC
pygame.mixer.music.load('music\interstellar-piano-157094.mp3    ')  
pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music on a loop (pass -1 for infinite loop)

BACKGROUND_IMG = pygame.image.load('imgs\space.jpg')
BACKGROUND_IMG_SCALED = pygame.transform.scale(BACKGROUND_IMG,(int(BACKGROUND_IMG.get_width() /3), int(BACKGROUND_IMG.get_height() /3.3)))

SUN_IMG = pygame.image.load('imgs\sun.png.png')
SUN_IMG_SCALED = pygame.transform.scale(SUN_IMG,(int(SUN_IMG.get_width() / 4), int(SUN_IMG.get_height() / 4)))

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans",16)


class TwinklingStar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_brightness = random.randint(100, 255)  # Base brightness of the star
        self.twinkle_speed = random.uniform(0.5, 1)  # Speed of twinkling
        self.phase = random.uniform(0, 2 * math.pi)  # Random phase for smooth twinkle

    def draw(self, win):
        # Calculate brightness with a sine wave
        brightness = self.base_brightness + int(50 * math.sin(pygame.time.get_ticks() * self.twinkle_speed + self.phase))
        brightness = max(0, min(255, brightness))  # Ensure brightness stays within 0-255 range
        color = (brightness, brightness, brightness)
        
        pygame.draw.circle(win, color, (self.x, self.y), 2)

class Particle:
    def __init__(self, x, y,color):
        self.x = x
        self.y = y 
        self.size = random.randint(2, 5)
        self.lifetime = random.randint(50,100)
        self.color = (*color[:3], 150) 
        self.x_vel = random.uniform(-0.5, 0.5)
        self.y_vel = random.uniform(-0.5, 0.5)

    def update(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.size -= 0.05
        self.lifetime -= 1
    
    def draw(self, win):
        if self.size > 0:
            pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), int(self.size))
    
class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 220 / AU #1AU = 100 pixels
    TIMESTEP = 360 * 24 #1 day
    
    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        
        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0
        
        self.x_vel = 0
        self.y_vel = 0 
        
        self.particles = []

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH/2
        y = self.y * self.SCALE + HEIGHT/2
        
        if True:
            self.update_particles(x,y)
        
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x,y))
            
            pygame.draw.lines(win, self.color, False, updated_points, 2)
        
        if self.sun:
            sun_rect = SUN_IMG_SCALED.get_rect(center=(x, y))  # Center the image on the sun's position
            win.blit(SUN_IMG_SCALED, sun_rect)
        else:
            pygame.draw.circle(win, self.color, (x,y), self.radius)
        
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000,1)}km", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y + distance_text.get_width()/10))
            
        
    def update_particles(self, x, y):
        if len(self.particles) < 100:
            self.particles.append(Particle(x, y, self.color))
        
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0 or particle.size <= 0:
                self.particles.remove(particle)
        
        for particle in self.particles:
            particle.draw(WIN)
        
    def atrraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        
        if other.sun:
            self.distance_to_sun = distance
            
        force = self.G * self.mass * other.mass / distance ** 2        
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x,force_y
    
    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            
            fx, fy = self.atrraction(planet)
            total_fx += fx
            total_fy +=fy
        
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP
        
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP

        self.orbit.append((self.x,self.y))
        
        
        
        
                
                
        
def main():
    run = True
    clock = pygame.time.Clock()
    
    twinkling_stars = [TwinklingStar(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
    
    #defining planets
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True
    
    earth = Planet(-1 * Planet.AU, 0, 12, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000 
    
    mars = Planet(-1.524 * Planet.AU, 0, 8, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000
    
    mercury = Planet(0.387 * Planet.AU, 0, 4, DARK_GREY, 3.30 * 10**23)
    mercury.y_vel = 47.4 * 1000
    
    venus = Planet(0.723 * Planet.AU, 0, 10, WHITE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000
    
    #jupiter = Planet(5.2 * Planet.AU, 0, 20, YELLOW, 1.898 * 10**27)
    #jupiter.y_vel = 13 * 1000
    planets = [sun, earth, mars, mercury, venus]
    
    while run:
        clock.tick(60)
        WIN.blit(BACKGROUND_IMG_SCALED, (0, 0))
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            #if event.type == pygame.KEYDOWN:
            #    run = False

        for star in twinkling_stars:
            star.draw(WIN)
        
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)
            
        pygame.display.update()
    pygame.quit()
    
main()
