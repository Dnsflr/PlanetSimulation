import pygame
import math
import random
pygame.init()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Planet Simulation")

#MUSIC
pygame.mixer.music.load('PlanetSim\music\interstellar-piano-157094.mp3')  
pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music on a loop (pass -1 for infinite loop)

BACKGROUND_IMG = pygame.image.load('PlanetSim\imgs\space.jpg')
BACKGROUND_IMG_SCALED = pygame.transform.scale(BACKGROUND_IMG,(int(BACKGROUND_IMG.get_width() /3), int(BACKGROUND_IMG.get_height() /3.3)))

SUN_IMG = pygame.image.load('PlanetSim\imgs\sun.png.png')
SUN_IMG_SCALED = pygame.transform.scale(SUN_IMG,(int(SUN_IMG.get_width() / 4), int(SUN_IMG.get_height() / 4)))

#COLORS
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
GREEN = (0, 250, 0)

FONT = pygame.font.SysFont("comicsans",16)

class UI:
    def __init__(self, planets, font):
       
        self.planets = planets  
        self.font = font 
        self.selected_planet_index = 0 
        self.selected_planet = self.planets[self.selected_planet_index]  
        self.pending_simulate = self.selected_planet.simulate  
        self.pending_mass = f"{self.selected_planet.mass:.4e}"  
        self.input_active = False  
        self.ui_visible = False  

    def draw(self, win):
        
        if self.ui_visible:  
           
            self.draw_background(win, WIDTH - 470, HEIGHT - 320, 450, 300)
            
            
            self.draw_element(win, f"Selected Planet: {self.selected_planet.name}", WIDTH - 450, HEIGHT - 300)

           
            sim_status = "Simulating" if self.selected_planet.simulate else "Not Simulating" 
            self.draw_element(win, "Simulate:", WIDTH - 450, HEIGHT - 260)  
            self.draw_element(win, sim_status, WIDTH - 250, HEIGHT - 260) 
            toggle_button = self.draw_button(win, "ON" if self.pending_simulate else "OFF", WIDTH - 120, HEIGHT - 260, 100, 30, GREEN if self.pending_simulate else RED)

           
            self.draw_element(win, "Mass:", WIDTH - 450, HEIGHT - 220) 
            self.draw_element(win, f"{self.selected_planet.mass:.4e}", WIDTH - 370, HEIGHT - 220) 
            mass_input_box = self.draw_textbox(win, WIDTH - 200, HEIGHT - 220, 150, 30, self.pending_mass)  

           
            ok_button = self.draw_button(win, "OK", WIDTH - 270, HEIGHT - 160, 100, 30, BLUE)

            
            exit_button = self.draw_button(win, "Exit Editor", WIDTH - 270, HEIGHT - 100, 150, 30, RED)

           
            return toggle_button, mass_input_box, ok_button, exit_button
        return None, None, None, None  

    def handle_controls(self, event, toggle_button, mass_input_box, ok_button, exit_button, edit_button):
        
        mouse_pos = pygame.mouse.get_pos()  

        if event.type == pygame.MOUSEBUTTONDOWN:
            if edit_button and edit_button.collidepoint(mouse_pos):  
                self.ui_visible = True  

            if self.ui_visible:  
                if toggle_button and toggle_button.collidepoint(mouse_pos): 
                    self.pending_simulate = not self.pending_simulate  

                if ok_button and ok_button.collidepoint(mouse_pos): 
                    self.selected_planet.simulate = self.pending_simulate  
                    try:
                        self.selected_planet.mass = float(self.pending_mass)  
                    except ValueError:
                        print("Invalid mass value.")  
                    self.input_active = False  

                if mass_input_box and mass_input_box.collidepoint(mouse_pos):  
                    self.input_active = True 

                if exit_button and exit_button.collidepoint(mouse_pos): 
                    self.ui_visible = False  

        if self.input_active and event.type == pygame.KEYDOWN and self.ui_visible:  
            if event.key == pygame.K_BACKSPACE:  
                self.pending_mass = self.pending_mass[:-1]
            elif event.key == pygame.K_RETURN:  
                self.input_active = False
            else:  
                self.pending_mass += event.unicode

    def draw_edit_button(self, win):
        if not self.ui_visible:  
            return self.draw_button(win, "Edit", WIDTH - 120, HEIGHT - 70, 100, 50, DARK_GREY)  
        return None

    def draw_element(self, win, text, x, y):
        label = self.font.render(text, 1, WHITE)  
        win.blit(label, (x, y)) 

    def draw_background(self, win, x, y, width, height):
        bg_rect = pygame.Surface((width, height))  
        bg_rect.set_alpha(180)  
        bg_rect.fill((50, 50, 50))  
        win.blit(bg_rect, (x, y))  

    def draw_button(self, win, text, x, y, width, height, color):
        
        button_rect = pygame.Rect(x, y, width, height)  
        pygame.draw.rect(win, color, button_rect) 
        label = self.font.render(text, 1, WHITE)  
        win.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))  
        return button_rect  

    def draw_textbox(self, win, x, y, width, height, text):
        
        textbox_rect = pygame.Rect(x, y, width, height)  
        pygame.draw.rect(win, DARK_GREY, textbox_rect)  
        label = self.font.render(text, 1, WHITE)  
        win.blit(label, (x + 5, y + 5))  
        return textbox_rect  

    def change_planet(self, direction):
        
        if direction == "next":
            self.selected_planet_index = (self.selected_planet_index + 1) % len(self.planets)  
        elif direction == "previous":
            self.selected_planet_index = (self.selected_planet_index - 1) % len(self.planets)  
        self.selected_planet = self.planets[self.selected_planet_index]  
        self.pending_simulate = self.selected_planet.simulate 
        self.pending_mass = f"{self.selected_planet.mass:.4e}"  

class TwinklingStar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_brightness = random.randint(100, 255)  
        self.twinkle_speed = random.uniform(0.5, 1)  
        self.phase = random.uniform(0, 2 * math.pi)  

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
    TIMESTEP = 260 * 24 #1 day
    #MAX_ORBIT_POINTS = 1000 #Max number of points holding in memory
    
    def __init__(self, name, x, y, radius, color, mass):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.simulate = True 
        
        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0
        
        self.x_vel = 0
        self.y_vel = 0 
        
        self.particles = []
        

    def draw(self, win):
        if not self.simulate:
            return #if planet is inactive skip drawing
        
        
        x = self.x * self.SCALE + WIDTH/2
        y = self.y * self.SCALE + HEIGHT/2
        
        if True:
            self.update_particles(x,y)
        
        if len(self.orbit) > 2:
            updated_points = []
            
            for point in self.orbit:
                x_orbit, y_orbit = point
                x_orbit = x_orbit * self.SCALE + WIDTH / 2
                y_orbit = y_orbit * self.SCALE + HEIGHT / 2
                updated_points.append((x_orbit, y_orbit))
            
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
        if not self.simulate or not other.simulate:
            return 0, 0# if either of planets is not simualted return 0, kinda obvious
        
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
        if not self.simulate:
            return
        
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

        
        self.orbit.append((self.x, self.y))
        
        #if len(self.orbit) > self.MAX_ORBIT_POINTS:
        #    self.orbit.pop(0)
     
def main():
    run = True
    clock = pygame.time.Clock()
    
    twinkling_stars = [TwinklingStar(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
    
    #defining planets
    sun = Planet('Sun',0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True
    
    earth = Planet('Earth',-1 * Planet.AU, 0, 12, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000 
    
    mars = Planet('Mars',-1.524 * Planet.AU, 0, 8, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000
    
    mercury = Planet('Mercury',0.387 * Planet.AU, 0, 4, DARK_GREY, 3.30 * 10**23)
    mercury.y_vel = 47.4 * 1000
    
    venus = Planet('Venus',0.723 * Planet.AU, 0, 10, WHITE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000
    
    jupiter = Planet('Jupiter',5.2 * Planet.AU, 0, 20, YELLOW, 1.898 * 10**27)
    jupiter.y_vel = 13 * 1000
    planets = [sun, earth, mars, mercury, venus]
    ui = UI(planets, FONT)
    
    while run:
        clock.tick(60)
        WIN.blit(BACKGROUND_IMG_SCALED, (0, 0))

        for star in twinkling_stars:
            star.draw(WIN)

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

       
        edit_button = ui.draw_edit_button(WIN)

        toggle_button, mass_input_box, ok_button, exit_button = ui.draw(WIN)  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                elif event.key == pygame.K_LEFT:  
                    ui.change_planet("previous")
                elif event.key == pygame.K_RIGHT:  
                    ui.change_planet("next")

        
            ui.handle_controls(event, toggle_button, mass_input_box, ok_button, exit_button, edit_button)

        pygame.display.update()
    
main()