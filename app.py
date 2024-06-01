import asyncio
import app
import gc
import display
import random

from .names import Names

from events.input import Buttons, BUTTON_TYPES
from app_components import Menu, Notification, clear_background
from app_components.tokens import clear_background, set_color
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable
import settings
from tildagonos import tildagonos, led_colours



class FerdiApp(app.App):
    def __init__(self):
        super().__init__()

        self.temp = 18.5
        self.humidity = 80

        self.menu = None
        self.led_update_counter = 0
        self.menu_update_counter = 0
        self.button_states = Buttons(self)
        self.notification = None
        self.data_list = []
        self.data_list_pos = 0
        self.led_pos = 0

        eventbus.emit(PatternDisable())

        for i in range(12):
            tildagonos.leds[i] = (0,0,0)

        self.update_list()
        self.activate_menu()

    def update(self, delta):
        self.menu.update(delta)

        self.led_update_counter += 1
        if self.led_update_counter > 2:
            tildagonos.leds[self.led_pos] = (0, 0, 0)
            self.led_pos = self.led_pos + 1 if self.led_pos < 12 else 0
            tildagonos.leds[self.led_pos] = (100, 0, 0)
            self.led_update_counter = 0

        self.menu_update_counter += 1
        if self.menu_update_counter > 15:
            if self.menu.position >= len(self.data_list)-1:
                self.update_list()
                self.activate_menu()
            else:
                # Tick menu
                self.menu.down_handler()
            self.menu_update_counter=0

        if self.notification:
            self.notification.update(delta)

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()

    def activate_menu(self):
        self.menu = Menu(
            self,
            menu_items=self.data_list,
            item_font_size=20,
            focused_item_font_size=40,
            # select_handler=self.select_handler,
            # change_handler=self.change_handler,
            back_handler=self.deactivate_menu
            # position=self.data_list_pos
        )

    def deactivate_menu(self):
        self.menu._cleanup()

    def update_list(self):
        self.data_list = ["Hi there", "i'm Ferdinand", f"Temp: {self.temp}C", f"Hum: {self.humidity}%"]

    def draw(self, ctx):
        clear_background(ctx)
        self.menu.draw(ctx)

        if self.notification:
            self.notification.draw(ctx)

    async def background_task(self):
        while True:
            await asyncio.sleep(1)

            print(
                "fps:",
                display.get_fps(),
                f"mem used: {gc.mem_alloc()}, mem free:{gc.mem_free()}",
            )

            self.temp = random.choice([16.0,16.5,17.0,17.5,18.0,18.5])
            self.humidity = random.choice([70,75,80,85])
            print(f"TEMP:{self.temp} HUM:{self.humidity}")

__app_export__ = FerdiApp
