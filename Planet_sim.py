import pygame
import math
import random
pygame.init()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

# Load and set up background music
pygame.mixer.music.load('PlanetSim/music/interstellar-piano-157094.mp3')  
pygame.mixer.music.set_volume(0.5)  
pygame.mixer.music.play(-1)  # Play the music in a loop

# Load and scale background image and sun image
BACKGROUND_IMG = pygame.image.load('PlanetSim/imgs/space.jpg')
BACKGROUND_IMG_SCALED = pygame.transform.scale(BACKGROUND_IMG, (int(BACKGROUND_IMG.get_width() / 3), int(BACKGROUND_IMG.get_height() / 3.3)))

SUN_IMG = pygame.image.load('PlanetSim/imgs/sun.png.png')
SUN_IMG_SCALED = pygame.transform.scale(SUN_IMG, (int(SUN_IMG.get_width() / 4), int(SUN_IMG.get_height() / 4)))

# Define colors used in the UI
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
GREEN = (0, 250, 0)

FONT = pygame.font.SysFont("comicsans", 16)

class UI:
    def __init__(self, planets, font):
        """Initialize UI with planets and font"""
        self.planets = planets  # List of planets to manage
        self.font = font  # Font used for text rendering
        self.selected_planet_index = 0  # Index of currently selected planet
        self.selected_planet = self.planets[self.selected_planet_index]  # Current planet selected for editing
        self.pending_simulate = self.selected_planet.simulate  # Pending simulation status for selected planet
        self.pending_mass = f"{self.selected_planet.mass:.4e}"  # Mass input to be modified
        self.input_active = False  # Track if mass input is active
        self.ui_visible = False  # UI visibility state

    def draw(self, win):
        """Draw the UI components if visible"""
        if self.ui_visible:
            # Draw semi-transparent UI background
            self.draw_background(win, WIDTH - 470, HEIGHT - 320, 450, 300)

            # Show selected planet's name
            self.draw_element(win, f"Selected Planet: {self.selected_planet.name}", WIDTH - 450, HEIGHT - 300)

            # Show simulation status and toggle button
            sim_status = "Simulating" if self.selected_planet.simulate else "Not Simulating"
            self.draw_element(win, "Simulate:", WIDTH - 450, HEIGHT - 260)
            self.draw_element(win, sim_status, WIDTH - 250, HEIGHT - 260)
            toggle_button = self.draw_button(win, "ON" if self.pending_simulate else "OFF", WIDTH - 120, HEIGHT - 260, 100, 30, GREEN if self.pending_simulate else RED)

            # Show current mass and textbox for editing it
            self.draw_element(win, "Mass:", WIDTH - 450, HEIGHT - 220)
            self.draw_element(win, f"{self.selected_planet.mass:.4e}", WIDTH - 370, HEIGHT - 220)
            mass_input_box = self.draw_textbox(win, WIDTH - 200, HEIGHT - 220, 150, 30, self.pending_mass)

            # OK button for confirming changes
            ok_button = self.draw_button(win, "OK", WIDTH - 270, HEIGHT - 160, 100, 30, BLUE)

            # Exit button to close the editor
            exit_button = self.draw_button(win, "Exit Editor", WIDTH - 270, HEIGHT - 100, 150, 30, RED)

            return toggle_button, mass_input_box, ok_button, exit_button

        return None, None, None, None

    def handle_controls(self, event, toggle_button, mass_input_box, ok_button, exit_button, edit_button):
        """Handle UI events such as clicks and input"""
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # When "Edit" button is clicked, make UI visible
            if edit_button and edit_button.collidepoint(mouse_pos):
                self.ui_visible = True

            if self.ui_visible:
                # Toggle planet simulation ON/OFF
                if toggle_button and toggle_button.collidepoint(mouse_pos):
                    self.pending_simulate = not self.pending_simulate

                # Confirm changes when OK button is clicked
                if ok_button and ok_button.collidepoint(mouse_pos):
                    self.selected_planet.simulate = self.pending_simulate
                    try:
                        self.selected_planet.mass = float(self.pending_mass)  # Set new mass
                    except ValueError:
                        print("Invalid mass value.")
                    self.input_active = False

                # Enable input editing when clicked on mass input box
                if mass_input_box and mass_input_box.collidepoint(mouse_pos):
                    self.input_active = True

                # Exit editor and hide UI
                if exit_button and exit_button.collidepoint(mouse_pos):
                    self.ui_visible = False

        # Handle mass input changes
        if self.input_active and event.type == pygame.KEYDOWN and self.ui_visible:
            if event.key == pygame.K_BACKSPACE:
                self.pending_mass = self.pending_mass[:-1]  # Remove last character
            elif event.key == pygame.K_RETURN:
                self.input_active = False  # Exit input mode when Enter is pressed
            else:
                self.pending_mass += event.unicode  # Add new character to mass input

    def draw_edit_button(self, win):
        """Draw the 'Edit' button when the UI is hidden"""
        if not self.ui_visible:
            return self.draw_button(win, "Edit", WIDTH - 120, HEIGHT - 70, 100, 50, DARK_GREY)
        return None

    def draw_element(self, win, text, x, y):
        """Draw any text element on the window"""
        label = self.font.render(text, 1, WHITE)
        win.blit(label, (x, y))

    def draw_background(self, win, x, y, width, height):
        """Draw the background for the UI"""
        bg_rect = pygame.Surface((width, height))
        bg_rect.set_alpha(180)  # Semi-transparent background
        bg_rect.fill((50, 50, 50))  # Gray color
        win.blit(bg_rect, (x, y))

    def draw_button(self, win, text, x, y, width, height, color):
        """Helper method to draw buttons"""
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(win, color, button_rect)
        label = self.font.render(text, 1, WHITE)
        win.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))  # Center text in button
        return button_rect

    def draw_textbox(self, win, x, y, width, height, text):
        """Helper method to draw a text box for input"""
        textbox_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(win, DARK_GREY, textbox_rect)
        label = self.font.render(text, 1, WHITE)
        win.blit(label, (x + 5, y + 5))  # Draw the input text
        return textbox_rect

    def change_planet(self, direction):
        """Change the selected planet based on direction"""
        if direction == "next":
            self.selected_planet_index = (self.selected_planet_index + 1) % len(self.planets)
        elif direction == "previous":
            self.selected_planet_index = (self.selected_planet_index - 1) % len(self.planets)
        self.selected_planet = self.planets[self.selected_planet_index]
        self.pending_simulate = self.selected_planet.simulate
        self.pending_mass = f"{self.selected_planet.mass:.4e}"

class TwinklingStar:
    def __init__(self, x, y):
        """Initialize a twinkling star"""
        self.x = x
        self.y = y
        self.base_brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.5, 1)
        self.phase = random.uniform(0, 2 * math.pi)

    def draw(self, win):
        """Draw a twinkling star with changing brightness"""
        brightness = self.base_brightness + int(50 * math.sin(pygame.time.get_ticks() * self.twinkle_speed + self.phase))
        brightness = max(0, min(255, brightness))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(win, color, (self.x, self.y), 2)

class Particle:
    def __init__(self, x, y, color):
        """Initialize a particle"""
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.lifetime = random.randint(50, 100)
        self.color = (*color[:3], 150)
        self.x_vel = random.uniform(-0.5, 0.5)
        self.y_vel = random.uniform(-0.5, 0.5)

    def update(self):
        """Update the particle's position and state"""
        self.x += self.x_vel
        self.y += self.y_vel
        self.size -= 0.05
        self.lifetime -= 1

    def draw(self, win):
        """Draw the particle"""
        if self.size > 0:
            pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), int(self.size))

class Planet:
    AU = 149.6e6 * 1000  # Astronomical Unit in meters
    G = 6.67428e-11  # Gravitational constant
    SCALE = 220 / AU  # 1AU = 100 pixels
    TIMESTEP = 260 * 24  # 1 day in seconds

    def __init__(self, name, x, y, radius, color, mass):
        """Initialize a planet with its attributes"""
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.simulate = True
        self.orbit = []  # Store the path of the planet's orbit
        self.sun = False
        self.distance_to_sun = 0
        self.x_vel = 0
        self.y_vel = 0
        self.particles = []  # Visual effect particles

    def draw(self, win):
        """Draw the planet and its orbit"""
        if not self.simulate:
            return  # Skip drawing if the planet is not active

        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        self.update_particles(x, y)  # Update visual particles

        if len(self.orbit) > 2:
            updated_points = [(x_orbit * self.SCALE + WIDTH / 2, y_orbit * self.SCALE + HEIGHT / 2) for x_orbit, y_orbit in self.orbit]
            pygame.draw.lines(win, self.color, False, updated_points, 2)  # Draw the orbit path

        if self.sun:
            sun_rect = SUN_IMG_SCALED.get_rect(center=(x, y))  # Center the sun image
            win.blit(SUN_IMG_SCALED, sun_rect)
        else:
            pygame.draw.circle(win, self.color, (x, y), self.radius)  # Draw the planet

    def update_particles(self, x, y):
        """Update the particles around the planet"""
        if len(self.particles) < 100:
            self.particles.append(Particle(x, y, self.color))

        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0 or particle.size <= 0:
                self.particles.remove(particle)

        for particle in self.particles:
            particle.draw(WIN)

    def atrraction(self, other):
        """Calculate the gravitational force between planets"""
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        """Update the planet's position based on gravitational forces"""
        if not self.simulate:
            return

        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.atrraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP

        self.orbit.append((self.x, self.y))

def main():
    """Main loop of the planet simulation"""
    run = True
    clock = pygame.time.Clock()

    # Generate twinkling stars in the background
    twinkling_stars = [TwinklingStar(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

    # Create planets with initial values
    sun = Planet('Sun', 0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    earth = Planet('Earth', -1 * Planet.AU, 0, 12, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000  # Earth's velocity

    mars = Planet('Mars', -1.524 * Planet.AU, 0, 8, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000

    mercury = Planet('Mercury', 0.387 * Planet.AU, 0, 4, DARK_GREY, 3.30 * 10**23)
    mercury.y_vel = 47.4 * 1000

    venus = Planet('Venus', 0.723 * Planet.AU, 0, 10, WHITE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000

    jupiter = Planet('Jupiter', 5.2 * Planet.AU, 0, 20, YELLOW, 1.898 * 10**27)
    jupiter.y_vel = 13 * 1000

    planets = [sun, earth, mars, mercury, venus]  # List of all planets
    ui = UI(planets, FONT)  # Initialize UI with the planets

    while run:
        clock.tick(60)  # Cap the frame rate at 60 FPS
        WIN.blit(BACKGROUND_IMG_SCALED, (0, 0))  # Draw background image

        # Draw stars
        for star in twinkling_stars:
            star.draw(WIN)

        # Update and draw planets
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        # Draw "Edit" button if UI is hidden
        edit_button = ui.draw_edit_button(WIN)

        # Draw the UI if it's visible
        toggle_button, mass_input_box, ok_button, exit_button = ui.draw(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Exit simulation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False  # Quit simulation on 'q' press
                elif event.key == pygame.K_LEFT:
                    ui.change_planet("previous")  # Select previous planet
                elif event.key == pygame.K_RIGHT:
                    ui.change_planet("next")  # Select next planet

            # Handle UI interactions
            ui.handle_controls(event, toggle_button, mass_input_box, ok_button, exit_button, edit_button)

        pygame.display.update()  # Update the display

main()
