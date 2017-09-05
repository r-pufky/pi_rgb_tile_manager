#
# Mass Transit Route Tile for Tile Manager.
#
# This tile will render a route with stop times to a tile.
#

import datetime
import pytz
from tile_manager import base_tile
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class RouteTile(base_tile.BaseTile):
  """ Tile used to handle routes and stops.

  Attributes:
    SHORT_TIME: datetime.timedelta any stop from now until this time delta
        are considered to be potentially 'missable' and colored differently.
        Default: 5 minutes.
    LONG_TIME: datetime.timedelta any stop from now + LONG_TIME are considered
        to be easy to catch, and are coloreed differently.
        Default: 10 minutes.
    TIME_FORMAT: String datetime strftime format for stops. Default: '%H:%M'.
    TIME_ZONE: pytz.timezone timezone to display time in.
        Default: 'America/Los_Angeles'.
    NUMBER_STOPS: Integer max number of stops to display for route. Default: 3.
    STOP_SEPARATOR: String separator for listing stops. Default: ', '.
    ROUTER_SEPARATOR: String separator for listing routes. Default: ': '.
  """
  SHORT_TIME = datetime.timedelta(minutes=5)
  LONG_TIME = datetime.timedelta(minutes=10)
  TIME_FORMAT = '%H:%M'
  TIME_ZONE = pytz.timezone('America/Los_Angeles')
  NUMBER_STOPS = 3
  STOP_SEPARATOR = ', '
  ROUTER_SEPARATOR = ': '

  def __init__(self, x=0, y=0, scrolling=(2,0), route_name, stops):
    """ Initalize route tile object.

    Args:
      x: Integer absolute X position of tile. Default: 0.
      y: Integer absolute Y position of tile. Default: 0.
      scrolling: Tuple (Integer: X, Integer: Y) containing scrolling
          information. Values are number of pixels to change at once along
          respective axis. Default: (2, 0) (scroll right).
      route_name: String route name.
      stops: List of Strings for next time on route.
    """
    base_tile.BaseTile.__init__(self, x, y, scrolling)
    self.route = route_name
    self.stops = stops

  def _GetRenderSize(self):
    """ Determines the total size of the information rendered within a tile.

    Information rendered may be bigger than the tile space allocated, so
    calculate that size. This is used to determine MaxFrames based on
    scrolling speeds.

    Returns:
      Tuple (Integer: X, Integer: Y) size of rendered information.
    """
    max_width = 0
    max_height = 0
    # wrong, this should be a combined list of everything.
    for stop_time in self.stops:
      (width, height) = self.FONT.getsize('%s%s' % (
          stop_time.astimezone(tz=self.TIME_ZONE).strftime(self.TIME_FORMAT),
          self.STOP_SEPARATOR))
      max_width = max(width, max_width)
      max_height = max(height, max_height)
    return (max_width, max_height)

  def Render(self):
    """ Returns Image buffer for tile to render.

    Render can be called multiple times, but it is not garanteed that a
    specific time has elapsed; meaning you have would have to determine
    to advance the frame before rendering.

    [route][rout separator][stop][stop separator][stop]

    Text is rendered based from the tile x/y absolute position.

    Returns:
      Image containing rendered tile to display.
    """
    self._image_draw((self.x, self.y + self.FONT_Y_OFFSET),
                     '%s%s' % (self.route, self.route_separator),
                     font=self.FONT,
                     fill=base_tile.WHITE)
    x = self.x + self.FONT.getsize('%s%s' % (self.route, self.route_separator))

    for index, stop in enumerate(self.stops):      
      fill = base_tile.GREEN
      time_delta = stop - NOW
      if time_delta < self.SHORT_TIME:
        fill = base_tile.RED
      elif time_delta < self.LONG_TIME:
        fill = base_tile.YELLOW
      if index > 0:
        self._image_draw((x + 1, self.y + self.FONT_Y_OFFSET + 8 - 2),
                         self.separator,
                         font=self.FONT,
                         fill=base_tile.GRAY)
        x += self.FONT.getsize(self.separator)[0]
      self._image_draw((x, self.y + self.FONT_Y_OFFSET + 8),
                       stop.astimezone(tz=self.TIME_ZONE).strftime(self.TIME_FORMAT),
                       font=self.FONT,
                       fill=fill)
    self.displayed = True
    return self._image_buffer