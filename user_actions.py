
from kivy.uix.relativelayout import RelativeLayout

def keyboard_closed(self):
    """
    Handle keyboard closure by unbinding events.
    """
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    """
    Handle key press events for horizontal movement.
    """
    if keycode[1] == 'left':
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        self.current_speed_x = -self.SPEED_X
    return True

def on_keyboard_up(self, keyboard, keycode):
    """
    Handle key release events to stop horizontal movement.
    """
    self.current_speed_x = 0
    return True

def on_touch_down(self, touch):
    """
    Handle touch events to control horizontal movement.
    """
    # what happens when you touch the screen
    if not self.game_over and self.started_game:
        self.current_speed_x = self.SPEED_X if touch.x < self.width / 2 else -self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_up(self, touch):
    """
    Stop horizontal movement when the touch ends.
    """
    # what happens when you remove your touch from the screen
    self.current_speed_x = 0
