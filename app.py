import asyncio
import app

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

        self.menu = None
        self.button_states = Buttons(self)
        self.notification = None
        self.data_list = ["Hi there", "i'm Ferdinand", "Temp: 18C", "HId: 80%"]
        self.data_list_pos = 0
        self.led_pos = 0

        eventbus.emit(PatternDisable())

        for i in range(12):
            tildagonos.leds[i] = (0,0,0)

        self.activate_menu()

    def update(self, delta):
        self.menu.update(delta)

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
            item_font_size=25,
            focused_item_font_size=50,
            # select_handler=self.select_handler,
            # change_handler=self.change_handler,
            back_handler=self.deactivate_menu
            # position=self.data_list_pos
        )

    def deactivate_menu(self):
        self.menu._cleanup()

    def draw(self, ctx):
        clear_background(ctx)
        self.menu.draw(ctx)

        if self.notification:
            self.notification.draw(ctx)

        """ctx.save()
        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0, 0).move_to(-80, 0).text("FerdiApp")
        ctx.restore()"""

    async def run(self, render_update):
        # Render initial state
        await render_update()

        while True:
            await asyncio.sleep(.1)


            tildagonos.leds[self.led_pos] = (0, 0, 0)
            self.led_pos = self.led_pos + 1 if self.led_pos < 12 else 0
            tildagonos.leds[self.led_pos] = (100, 0, 0)

            # Tick menu
            #self.menu.down_handler()

            """# Create a yes/no dialogue, add it to the overlays
            dialog = YesNoDialog("Change the colour?", self)
            self.overlays = [dialog]
            # Wait for an answer from the dialogue, and if it was yes, randomise colour
            if await dialog.run(render_update):
                self.color = (random.random(), random.random(), random.random())

            # Remove the dialogue and re-render
            self.overlays = []"""

            await render_update()

"""
    async def background_task(self):
        while True:
            await asyncio.sleep(1)

            print(
                "fps:",
                display.get_fps(),
                f"mem used: {gc.mem_alloc()}, mem free:{gc.mem_free()}",
            )
"""

__app_export__ = FerdiApp
