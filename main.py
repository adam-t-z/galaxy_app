"""
Galaxy Game:
3D game created with Kivy framework for building cross-platform applications
Using python
"""

from kivy.config import Config

# Configure the application window size
#   When using Config.set() to set the window's width and height in a Kivy application,
#   it must be called before any other Kivy module is imported.

Config.set('graphics', 'width', '1200')  # Set the window width to 900px
Config.set('graphics', 'height', '800')  # Set the window height to 400px

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
import random

from kivy.lang.builder import Builder
from kivy.core.audio import SoundLoader

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform
    from user_actions import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed
    # Perspective point properties to create a 3D-like effect
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # Number of vertical and horizontal lines in the grid
    num_vertical_lines = 16
    num_horizontal_lines = 8

    # Spacing between lines as a percentage of screen size
    vertical_line_spacing = 0.3  # Spacing between vertical lines (relative to screen width)
    horizontal_line_spacing = 0.2  # Spacing between horizontal lines (relative to screen height)

    # Lists to store line objects for drawing
    vertical_lines = []
    horizontal_lines = []

    # Movement speeds and offsets
    SPEED = 1  # Speed of vertical movement
    current_offset_y = 0  # Vertical offset for scrolling
    # y_loop also determines the score
    current_y_loop = 0  # Determine how many times a horizontal line went down

    SPEED_X = 3  # Speed of horizontal movement
    current_offset_x = 0  # Horizontal offset for scrolling
    current_speed_x = 0  # Current horizontal speed

    num_tiles = 12
    tiles = []
    tiles_coordinates = []

    ship = None
    # store coordinates before transformation
    ship_coordinates = [(0,0),(0,0),(0,0)]
    ship_width = 0.1 # relative to screen width
    ship_height = 0.035 # relative to screen height
    ship_base_y = 0.04 # how far is the ship from the bottom of the screen

    game_over = False
    started_game = False

    menu_title = StringProperty("G  A  L  A  X  Y")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty()

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize components
        self.init_audio()
        self.init_lines()
        self.init_tiles()
        self.init_ship()
        self.straight_path_tile_coordinates()  # Generate straight path
        self.generate_tiles_coordinates()
        

        # Enable keyboard controls if the app is running on a desktop
        if self.is_desktop():
            # Request keyboard input
            self._keyboard = Window.request_keyboard(self.keyboard_closed,
                                                     self)
            # Bind keyboard events for key presses and releases
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        # Schedule the update function to run 60 times per second
        Clock.schedule_interval(self.update, 1 / 60)

        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = 0.25
        self.sound_galaxy.volume = 0.25
        self.sound_gameover_impact.volume = 0.15
        self.sound_gameover_voice.volume = 0.25
        self.sound_restart.volume = 0.25

    def reset_game(self):
        # self.sound_restart.play()
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.score_txt = "SCORE: 0"

        self.tiles_coordinates = []
        self.straight_path_tile_coordinates()  
        self.generate_tiles_coordinates()

        self.game_over = False

        # you can call this reset_game function in the init function go to 5:19:20

    def is_desktop(self):
        """
        Check if the app is running on a desktop platform.
        """
        # if is a mobile return False
        return platform in ('linux', 'win', 'macosx')

    def init_ship(self):
        with self.canvas:
            Color(0,0,0)
            self.ship = Triangle()
    
    def ship_on_path(self):
        """
        Return True if ship on_track
        """
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            
            # check if ti_y is greater than the first two horizontal lines:
            if ti_y > self.current_y_loop + 1:
                return False
            if self.ship_collided_with_tile(ti_x, ti_y):
                return True

        return False

    def ship_collided_with_tile(self, ti_x, ti_y):
        """
        Return True if ship is on tile -given its coordinates-
        """
        # coordinates of wanted tile:
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        
        # loop on all three points of ship and check if they are inside the tile coordinates:
        for i in range(3): 
            x,y = self.ship_coordinates[i]
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return True

        return False

    def update_ship(self):
        """
        Update coordinates of ship when resizing the screen, however, the ship is not moving, but the land is.
        """
        center_x = self.width//2
        ship_half_width = self.ship_width*self.width//2
        ship_base_y = self.height*self.ship_base_y

        self.ship_coordinates[0] = (center_x-ship_half_width, ship_base_y )
        self.ship_coordinates[1] = (center_x+ship_half_width , ship_base_y)
        self.ship_coordinates[2] = (center_x,  ship_base_y+self.height*self.ship_height)
        
        x1,y1 = self.transform( *self.ship_coordinates[0]) # put a * before to expand the tuple so it gives two arguments
        x2,y2 = self.transform( *self.ship_coordinates[1])
        x3,y3 = self.transform( *self.ship_coordinates[2])

        self.ship.points = [x1,y1,  x2,y2,  x3,y3]

    def init_lines(self):
        """
        Initialize vertical and horizontal lines for the grid.
        """
        with self.canvas:
            Color(1, 1, 1)  # Set line color to white
            # Create vertical lines
            self.vertical_lines = [
                Line(width=1.2) for _ in range(self.num_vertical_lines)
            ]
            # Create horizontal lines
            self.horizontal_lines = [
                Line(width=1.2) for _ in range(self.num_horizontal_lines)
            ]

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.num_tiles):
                self.tiles.append(Quad())

    def straight_path_tile_coordinates(self):
        """
        Generate 10 tiles in straight line only once at the beginning.
        Before any random tile generation.
        """
        for i in range(10):  # 10 straight tiles
            self.tiles_coordinates.append((0, i))  # (0, i) for a straight path

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0

        # Retain tiles within the visible range
        for i in range(  len(self.tiles_coordinates)-1 , -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            # get ycor of last tile in list
            last_x = self.tiles_coordinates[-1][0]
            last_y = self.tiles_coordinates[-1][1] + 1

        # Start random generation after straight path
        for i in range(len(self.tiles_coordinates), self.num_tiles):
            # 0->straight  1-> right  2-> left
            r  = random.randint(0,2)

            # Always increment y
            self.tiles_coordinates.append((last_x, last_y))

            # Ensure tiles stay within bounds
            end_index = self.num_vertical_lines//2-1
            start_index = -self.num_vertical_lines//2+1
            if last_x >= end_index:
                r=2 # Force left
            elif last_x <= start_index:
                r=1 # Force right

            if r==1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif r==2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            
            
            last_y += 1

    def update_tiles(self):
        for i in range(0, self.num_tiles):
            point = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(point[0], point[1])
            xmax, ymax = self.get_tile_coordinates(point[0] + 1, point[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def get_line_x_from_index(self, index):
        """
            Return xcor for vertical lines given their index.
            if four lines, then indices are [-1 0 1 2]
        """
        central_x = self.perspective_point_x
        spacing = self.vertical_line_spacing * self.width
        # current_offset_x is a global offset from player when moving
        line_x = central_x + (spacing * (index - 0.5)) + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        """
            Return ycor for horizontal lines given their index.
            if four lines, then indices are [0 1 2 3]
        """
        spacing_y = self.horizontal_line_spacing * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        # to make tile decrease every time we loop - looping means making horizontal line go below screen
        ti_y = ti_y - self.current_y_loop

        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)

        return x, y

    def update_lines(self):
        """
            Update the positions of the vertical and horizontal lines based on offsets and perspective.
        """

        start_index = -self.num_vertical_lines // 2 + 1
        end_index = start_index + self.num_vertical_lines - 1
        # Calculate x-coordinates for the first and last vertical lines
        # add current_offset_x so that horizontal lines stay within vertical ones
        first_x = self.get_line_x_from_index(start_index)
        last_x = self.get_line_x_from_index(end_index)

        # Update vertical lines

        for i in range(start_index, start_index + self.num_vertical_lines):
            x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(x, 0)  # Transform starting point
            x2, y2 = self.transform(x, self.height)  # Transform ending point
            self.vertical_lines[i].points = [x1, y1, x2, y2]  # Update line points

        # Update horizontal lines
        for i, line in enumerate(self.horizontal_lines):
            y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(first_x,  y)  # Start at the first vertical line
            x2, y2 = self.transform(last_x, y)  # End at the last vertical line

            line.points = [x1, y1, x2, y2]  # Update line points

    def update(self, dt):
        """
        Update the positions of the lines based on time and offsets.
        """
        # to make the time update 60 times per second
        time_factor = dt * 60  # Scale time to match 60 FPS

        if not self.game_over and self.started_game:
            # to make the y speed depend on the height of the screen
            speed_y = self.SPEED*self.height/100
            # Store the current offset before updating
            previous_offset_y = self.current_offset_y
            # the following line creates the looping effect when the offset_y is zero (e.g.) 400%40=0
            self.current_offset_y = (self.current_offset_y + speed_y *time_factor) % (self.horizontal_line_spacing * self.height)
        
            # Check if the offset wrapped around (a line "fell" off the screen)
            if self.current_offset_y < previous_offset_y:
                self.current_y_loop += 1
                self.generate_tiles_coordinates()
                self.score_txt = f"SCORE: {self.current_y_loop}"

            # to make the x speed depend on the height of the screen
            speed_x = self.current_speed_x*self.width/100
            self.current_offset_x += speed_x * time_factor

        self.update_lines()  # Update all line positions
        self.update_tiles()
        self.update_ship()
        
        if not self.ship_on_path() and not self.game_over:
            self.game_over = True
            self.menu_title = "G  A  M  E   O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            print("Game Over")

            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_gameover_voice, 1)
    
    def play_gameover_voice(self, dts):
        if self.game_over:
            self.sound_gameover_voice.play()

    def pressed_menu_button(self):
        print("Menu Button Pressed")
        # Start music1.wav from 20 seconds of music track
        if self.sound_music1:
            self.sound_music1.seek(20)
        self.sound_music1.play()

        if self.game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        
        

        self.reset_game()
        self.started_game = True
        self.menu_widget.opacity = 0

            

class GalaxyApp(App):
    """
    Main application class.
    """
    pass


# Run the app
GalaxyApp().run()
