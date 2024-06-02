import asyncio
import os

import app
import gc
import display
import random
import requests

from .names import Names
from typing import Any

from events.input import Buttons, BUTTON_TYPES
from app_components import Menu, Notification, clear_background
from app_components.tokens import clear_background, set_color
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable
import settings
from tildagonos import tildagonos, led_colours

os.open('xxx').

class FerdiApp(app.App):
    def __init__(self):
        super().__init__()

        self.weather_data = None
        self.temp = 18.5
        self.humidity = 80

        self.menu = None
        self.led_update_counter = 0
        self.menu_update_counter = 0
        self.button_states = Buttons(self)
        self.notification = None
        self.data_list = []
        self.data_list_pos = 0
        self.led_pos = 1

        eventbus.emit(PatternDisable())

        for i in range(12):
            tildagonos.leds[i+1] = (0,0,0)

        self.update_list()
        self.activate_menu()

    def update(self, delta):
        self.menu.update(delta)

        self.led_update_counter += 1
        if self.led_update_counter > 2:
            tildagonos.leds[self.led_pos] = (10, 0, 0)
            self.led_pos = self.led_pos + 1 if self.led_pos < 12 else 0
            tildagonos.leds[self.led_pos] = (255, 0, 0)
            tildagonos.leds[self.led_pos] = (100, 0, 0)
            self.led_update_counter = 1

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

    def try_connect(self):
        self.text = "Connecting to wifi"
        try:
            import wifi

            wifi.connect()
            self.text = "Connected to wifi"
        except ImportError as e:
            self.text = "Wifi failure"
            raise e

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

    def fetch_weather_data(self):
        print("Fetching weather data")

        # https://openweathermap.org/current
        api_key = open("./apps/example/api_key.txt", "r").read().strip()
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        units = "metric"
        emf_lat_long = (52.039554, -2.378344)

        final_url = (
                base_url
                + "lat="
                + str(emf_lat_long[0])
                + "&lon="
                + str(emf_lat_long[1])
                + "&appid="
                + api_key
                + "&units="
                + units
        )

        current_data: dict[Any, Any] = {}

        response = requests.get(final_url)
        current_data = response.json()

        if current_data:
            weather = WeatherInfo.from_json(current_data)
            self.weather_data = weather.human_readable()
        else:
            print("Error fetching weather data")
            raise Exception("Error fetching weather data")


class WeatherType:
    id: int
    main: str
    description: str
    icon: str

    @staticmethod
    def from_json(data: dict[str, Any]):
        weather_type = WeatherType()
        weather_type.id = data["id"]
        weather_type.main = data["main"]
        weather_type.description = data["description"]
        weather_type.icon = data["icon"]
        return weather_type


class WeatherInfo:
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    weather: WeatherType

    @staticmethod
    def from_json(data: dict[str, Any]):
        main = data["main"]
        weather_info = WeatherInfo()
        weather_info.temp = main["temp"]
        weather_info.weather = WeatherType.from_json(data["weather"][0])
        return weather_info

    def human_readable(self):
        return f"{self.weather.main}, {round(self.temp, 1)}°C"



__app_export__ = FerdiApp
