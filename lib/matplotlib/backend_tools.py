"""
Abstract base classes define the primitives for Tools.
These tools are used by `NavigationBase`

:class:`ToolBase`
    Simple tool that is instantiated every time it is used

:class:`ToolPersistentBase`
    Tool which instance is registered within `Navigation`

:class:`ToolToggleBase`
    PersistentTool that has two states, only one Toggle tool can be
    active at any given time for the same `Navigation`
"""


from matplotlib import rcParams
from matplotlib._pylab_helpers import Gcf
import numpy as np


class Cursors:
    # this class is only used as a simple namespace
    HAND, POINTER, SELECT_REGION, MOVE = list(range(4))
cursors = Cursors()


class ToolBase(object):
    """Base tool class

    Attributes
    ----------
    navigation : `NavigationBase`
        Navigation that controls this Tool
    figure : `FigureCanvas`
        Figure instance that is affected by this Tool
    """

    keymap = None
    """Keymap to associate this tool

    **string**: List of comma separated keys that will be used to call this
    tool when the keypress event of *self.figure.canvas* is emited
    """

    position = None
    """Where to put the tool in the *Toolbar*

     * **integer** : Position within the Toolbar
     * **None** : Do not put in the Toolbar
     * **-1**: At the end of the Toolbar

    """

    description = None
    """Description of the Tool

    **string**: If the Tool is included in the Toolbar this text is used
    as Tooltip
    """

    name = None
    """Name of the Tool

    **string**: Used as ID for the tool, must be unique
    """

    image = None
    """Filename of the image

    **string**: Filename of the image to use in the toolbar. If None, the
    `name` is used as label in the toolbar button
    """

    toggle = False  # Change the status (take control of the events)
    """Is toggleable tool

    **bool**:

     * **True**: The tool is a toogleable tool
     * **False**: The tool is not toggleable

    """

    persistent = False
    """Is persistent tool

    **bool**:
     * `True`: The tool is persistent
     * `False`: The tool is not persistent
    """

    cursor = None
    """Cursor to use when the tool is active
    """

    def __init__(self, figure, event=None):
        self.figure = figure
        self.navigation = figure.canvas.manager.navigation
        self.activate(event)

    def activate(self, event):
        """Called when tool is used

        Parameters
        ----------
        event : `Event`
            Event that caused this tool to be called
        """
        pass


class ToolPersistentBase(ToolBase):
    """Persisten tool

    Persistent Tools are keept alive after their initialization,
    a reference of the instance is kept by `navigation`.

    Notes
    -----
    The difference with `ToolBase` is that `activate` method
    is not called automatically at initialization
    """
    persistent = True

    def __init__(self, figure, event=None):
        self.figure = figure
        self.navigation = figure.canvas.manager.navigation
        #persistent tools don't call activate a at instantiation

    def unregister(self, *args):
        """Unregister the tool from the instances of Navigation

        If the reference in navigation was the last reference
        to the instance of the tool, it will be garbage collected
        """
        #call this to unregister from navigation
        self.navigation.unregister(self.name)


class ToolToggleBase(ToolPersistentBase):
    """Toggleable tool

    This tool is a Persistent Tool, that has the ability to capture
    the keypress, press and release events, preventing other tools
    to use the same events at the same time
    """
    toggle = True

    def mouse_move(self, event):
        """Mouse move event

        Called when a motion_notify_event is emited by the `FigureCanvas` if
        `navigation.movelock(self)` was setted
        """
        pass

    def press(self, event):
        """Mouse press event

        Called when a button_press_event is emited by the `FigureCanvas` if
        `navigation.presslock(self)` was setted
        """
        pass

    def release(self, event):
        """Mouse release event

        Called when a button_release_event is emited by the `FigureCanvas` if
        `navigation.releaselock(self)` was setted
        """
        pass

    def deactivate(self, event=None):
        """Deactivate the toggle tool

        This method is called when the tool is deactivated (second click on the
        toolbar button) or when another toogle tool from the same `navigation` is
        activated
        """
        pass

    def key_press(self, event):
        """Key press event

        Called when a key_press_event is emited by the `FigureCanvas` if
        `navigation.keypresslock(self)` was setted
        """
        pass


class ToolQuit(ToolBase):
    """Tool to call the figure manager destroy method
    """
    name = 'Quit'
    description = 'Quit the figure'
    keymap = rcParams['keymap.quit']

    def activate(self, event):
        Gcf.destroy_fig(self.figure)


class ToolEnableAllNavigation(ToolBase):
    """Tool to enable all axes for navigation interaction
    """
    name = 'EnableAll'
    description = 'Enables all axes navigation'
    keymap = rcParams['keymap.all_axes']

    def activate(self, event):
        if event.inaxes is None:
            return

        for a in self.figure.get_axes():
            if event.x is not None and event.y is not None \
                    and a.in_axes(event):
                a.set_navigate(True)


#FIXME: use a function instead of string for enable navigation
class ToolEnableNavigation(ToolBase):
    """Tool to enable a specific axes for navigation interaction
    """
    name = 'EnableOne'
    description = 'Enables one axes navigation'
    keymap = range(1, 10)

    def activate(self, event):
        if event.inaxes is None:
            return

        n = int(event.key) - 1
        for i, a in enumerate(self.figure.get_axes()):
            # consider axes, in which the event was raised
            # FIXME: Why only this axes?
            if event.x is not None and event.y is not None \
                    and a.in_axes(event):
                    a.set_navigate(i == n)


class ToolToggleGrid(ToolBase):
    """Tool to toggle the grid of the figure"""
    name = 'Grid'
    description = 'Toogle Grid'
    keymap = rcParams['keymap.grid']

    def activate(self, event):
        if event.inaxes is None:
            return
        event.inaxes.grid()
        self.figure.canvas.draw()


class ToolToggleFullScreen(ToolBase):
    """Tool to toggle full screen"""
    name = 'Fullscreen'
    description = 'Toogle Fullscreen mode'
    keymap = rcParams['keymap.fullscreen']

    def activate(self, event):
        self.figure.canvas.manager.full_screen_toggle()


class ToolToggleYScale(ToolBase):
    """Tool to toggle between linear and logarithmic the Y axis"""
    name = 'YScale'
    description = 'Toogle Scale Y axis'
    keymap = rcParams['keymap.yscale']

    def activate(self, event):
        ax = event.inaxes
        if ax is None:
            return

        scale = ax.get_yscale()
        if scale == 'log':
            ax.set_yscale('linear')
            ax.figure.canvas.draw()
        elif scale == 'linear':
            ax.set_yscale('log')
            ax.figure.canvas.draw()


class ToolToggleXScale(ToolBase):
    """Tool to toggle between linear and logarithmic the X axis"""
    name = 'XScale'
    description = 'Toogle Scale X axis'
    keymap = rcParams['keymap.xscale']

    def activate(self, event):
        ax = event.inaxes
        if ax is None:
            return

        scalex = ax.get_xscale()
        if scalex == 'log':
            ax.set_xscale('linear')
            ax.figure.canvas.draw()
        elif scalex == 'linear':
            ax.set_xscale('log')
            ax.figure.canvas.draw()


class ToolHome(ToolBase):
    """Restore the original view"""
    description = 'Reset original view'
    name = 'Home'
    image = 'home'
    keymap = rcParams['keymap.home']
    position = -1

    def activate(self, *args):
        self.navigation.views.home()
        self.navigation.positions.home()
        self.navigation.update_view()
#        self.set_history_buttons()


class ToolBack(ToolBase):
    """move back up the view lim stack"""
    description = 'Back to  previous view'
    name = 'Back'
    image = 'back'
    keymap = rcParams['keymap.back']
    position = -1

    def activate(self, *args):
        self.navigation.views.back()
        self.navigation.positions.back()
#        self.set_history_buttons()
        self.navigation.update_view()


class ToolForward(ToolBase):
    """Move forward in the view lim stack"""
    description = 'Forward to next view'
    name = 'Forward'
    image = 'forward'
    keymap = rcParams['keymap.forward']
    position = -1

    def activate(self, *args):
        self.navigation.views.forward()
        self.navigation.positions.forward()
#        self.set_history_buttons()
        self.navigation.update_view()


class ConfigureSubplotsBase(ToolPersistentBase):
    """Base tool for the configuration of subplots"""
    description = 'Configure subplots'
    name = 'Subplots'
    image = 'subplots'
    position = -1


class SaveFigureBase(ToolBase):
    """Base tool for figure saving"""
    description = 'Save the figure'
    name = 'Save'
    image = 'filesave'
    position = -1
    keymap = rcParams['keymap.save']


class ToolZoom(ToolToggleBase):
    """Zoom to rectangle"""
    description = 'Zoom to rectangle'
    name = 'Zoom'
    image = 'zoom_to_rect'
    position = -1
    keymap = rcParams['keymap.zoom']
    cursor = cursors.SELECT_REGION

    def __init__(self, *args):
        ToolToggleBase.__init__(self, *args)
        self._ids_zoom = []
        self._button_pressed = None
        self._xypress = None

    def activate(self, event):
        self.navigation.canvaslock(self)
        self.navigation.presslock(self)
        self.navigation.releaselock(self)

    def deactivate(self, event):
        self.navigation.canvaslock.release(self)
        self.navigation.presslock.release(self)
        self.navigation.releaselock.release(self)

    def press(self, event):
        """the press mouse button in zoom to rect mode callback"""
        # If we're already in the middle of a zoom, pressing another
        # button works to "cancel"
        if self._ids_zoom != []:
            self.navigation.movelock.release(self)
            for zoom_id in self._ids_zoom:
                self.figure.canvas.mpl_disconnect(zoom_id)
            self.navigation.release(event)
            self.navigation.draw()
            self._xypress = None
            self._button_pressed = None
            self._ids_zoom = []
            return

        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        # TODO: add a set home in navigation
        if self.navigation.views.empty():
            self.navigation.push_current()

        self._xypress = []
        for i, a in enumerate(self.figure.get_axes()):
            if (x is not None and y is not None and a.in_axes(event) and
                    a.get_navigate() and a.can_zoom()):
                self._xypress.append((x, y, a, i, a.viewLim.frozen(),
                                      a.transData.frozen()))

        self.navigation.movelock(self)
        id2 = self.figure.canvas.mpl_connect('key_press_event',
                                      self._switch_on_zoom_mode)
        id3 = self.figure.canvas.mpl_connect('key_release_event',
                                      self._switch_off_zoom_mode)

        self._ids_zoom = id2, id3
        self._zoom_mode = event.key

        self.navigation.press(event)

    def _switch_on_zoom_mode(self, event):
        self._zoom_mode = event.key
        self.mouse_move(event)

    def _switch_off_zoom_mode(self, event):
        self._zoom_mode = None
        self.mouse_move(event)

    def mouse_move(self, event):
        """the drag callback in zoom mode"""
        if self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, _ind, _lim, _trans = self._xypress[0]

            # adjust x, last, y, last
            x1, y1, x2, y2 = a.bbox.extents
            x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
            y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)

            if self._zoom_mode == "x":
                x1, y1, x2, y2 = a.bbox.extents
                y, lasty = y1, y2
            elif self._zoom_mode == "y":
                x1, y1, x2, y2 = a.bbox.extents
                x, lastx = x1, x2

            self.navigation.draw_rubberband(event, x, y, lastx, lasty)

    def release(self, event):
        """the release mouse button callback in zoom to rect mode"""
        self.navigation.movelock.release(self)
        for zoom_id in self._ids_zoom:
            self.figure.canvas.mpl_disconnect(zoom_id)
        self._ids_zoom = []

        if not self._xypress:
            return

        last_a = []

        for cur_xypress in self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, _ind, lim, _trans = cur_xypress
            # ignore singular clicks - 5 pixels is a threshold
            if abs(x - lastx) < 5 or abs(y - lasty) < 5:
                self._xypress = None
                self.navigation.release(event)
                self.navigation.draw()
                return

            x0, y0, x1, y1 = lim.extents

            # zoom to rect
            inverse = a.transData.inverted()
            lastx, lasty = inverse.transform_point((lastx, lasty))
            x, y = inverse.transform_point((x, y))
            Xmin, Xmax = a.get_xlim()
            Ymin, Ymax = a.get_ylim()

            # detect twinx,y axes and avoid double zooming
            twinx, twiny = False, False
            if last_a:
                for la in last_a:
                    if a.get_shared_x_axes().joined(a, la):
                        twinx = True
                    if a.get_shared_y_axes().joined(a, la):
                        twiny = True
            last_a.append(a)

            if twinx:
                x0, x1 = Xmin, Xmax
            else:
                if Xmin < Xmax:
                    if x < lastx:
                        x0, x1 = x, lastx
                    else:
                        x0, x1 = lastx, x
                    if x0 < Xmin:
                        x0 = Xmin
                    if x1 > Xmax:
                        x1 = Xmax
                else:
                    if x > lastx:
                        x0, x1 = x, lastx
                    else:
                        x0, x1 = lastx, x
                    if x0 > Xmin:
                        x0 = Xmin
                    if x1 < Xmax:
                        x1 = Xmax

            if twiny:
                y0, y1 = Ymin, Ymax
            else:
                if Ymin < Ymax:
                    if y < lasty:
                        y0, y1 = y, lasty
                    else:
                        y0, y1 = lasty, y
                    if y0 < Ymin:
                        y0 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                else:
                    if y > lasty:
                        y0, y1 = y, lasty
                    else:
                        y0, y1 = lasty, y
                    if y0 > Ymin:
                        y0 = Ymin
                    if y1 < Ymax:
                        y1 = Ymax

            if self._button_pressed == 1:
                if self._zoom_mode == "x":
                    a.set_xlim((x0, x1))
                elif self._zoom_mode == "y":
                    a.set_ylim((y0, y1))
                else:
                    a.set_xlim((x0, x1))
                    a.set_ylim((y0, y1))
            elif self._button_pressed == 3:
                if a.get_xscale() == 'log':
                    alpha = np.log(Xmax / Xmin) / np.log(x1 / x0)
                    rx1 = pow(Xmin / x0, alpha) * Xmin
                    rx2 = pow(Xmax / x0, alpha) * Xmin
                else:
                    alpha = (Xmax - Xmin) / (x1 - x0)
                    rx1 = alpha * (Xmin - x0) + Xmin
                    rx2 = alpha * (Xmax - x0) + Xmin
                if a.get_yscale() == 'log':
                    alpha = np.log(Ymax / Ymin) / np.log(y1 / y0)
                    ry1 = pow(Ymin / y0, alpha) * Ymin
                    ry2 = pow(Ymax / y0, alpha) * Ymin
                else:
                    alpha = (Ymax - Ymin) / (y1 - y0)
                    ry1 = alpha * (Ymin - y0) + Ymin
                    ry2 = alpha * (Ymax - y0) + Ymin

                if self._zoom_mode == "x":
                    a.set_xlim((rx1, rx2))
                elif self._zoom_mode == "y":
                    a.set_ylim((ry1, ry2))
                else:
                    a.set_xlim((rx1, rx2))
                    a.set_ylim((ry1, ry2))

        self.navigation.draw()
        self._xypress = None
        self._button_pressed = None

        self._zoom_mode = None

        self.navigation.push_current()
        self.navigation.release(event)


class ToolPan(ToolToggleBase):
    """Pan axes with left mouse, zoom with right"""
    keymap = rcParams['keymap.pan']
    name = 'Pan'
    description = 'Pan axes with left mouse, zoom with right'
    image = 'move'
    position = -1
    cursor = cursors.MOVE

    def __init__(self, *args):
        ToolToggleBase.__init__(self, *args)
        self._button_pressed = None
        self._xypress = None

    def activate(self, event):
        self.navigation.canvaslock(self)
        self.navigation.presslock(self)
        self.navigation.releaselock(self)

    def deactivate(self, event):
        self.navigation.canvaslock.release(self)
        self.navigation.presslock.release(self)
        self.navigation.releaselock.release(self)

    def press(self, event):
        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        #TODO: add define_home in navigation
        if self.navigation.views.empty():
            self.navigation.push_current()

        self._xypress = []
        for i, a in enumerate(self.figure.get_axes()):
            if (x is not None and y is not None and a.in_axes(event) and
                    a.get_navigate() and a.can_pan()):
                a.start_pan(x, y, event.button)
                self._xypress.append((a, i))
                self.navigation.movelock(self)
        self.navigation.press(event)

    def release(self, event):
        if self._button_pressed is None:
            return

        self.navigation.movelock.release(self)

        for a, _ind in self._xypress:
            a.end_pan()
        if not self._xypress:
            return
        self._xypress = []
        self._button_pressed = None
        self.navigation.push_current()
        self.navigation.release(event)
        self.navigation.draw()

    def mouse_move(self, event):
        for a, _ind in self._xypress:
            #safer to use the recorded button at the press than current button:
            #multiple button can get pressed during motion...
            a.drag_pan(self._button_pressed, event.key, event.x, event.y)
        self.navigation.dynamic_update()