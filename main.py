"""
Main module
"""
import os
import util.const as const

from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

from generator.fishbone_generator import FishBoneGenerator
from generator.fishbone import Pos
from loader.xml_loader import XMLLoader
from painter.diagram_painter import DiagramPainter
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from saver.pptx_saver import PPTXSaver
from saver.svg_saver import SVGSaver
from saver.png_saver import PNGSaver
from kivy.uix.image import Image
from kivy.config import Config

const.DEG = 30
const.VERTICAL_MARGIN = 60
const.HORIZONTAL_MARGIN = 100
const.HEIGHT = 30
const.WIDTH = 100
const.VERTICAL_BONE_ADD = 10

const.DIAGRAM_X = 500
const.DIAGRAM_Y = 400
const.MAIN_BONE_WIDTH = 10
const.MAIN_SUB_BONE_COLOR = (.16, .26, .63)
const.MAIN_BONE_TEXT_COLOR = (.46, .13, .16)


class PopupSaveMenu(BoxLayout):
    """ Save menu """
    popup_close = ObjectProperty(None)
    show_save = ObjectProperty(None)


class LoadDialog(FloatLayout):
    """ Load Dialog """
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    """ Save Dialog """
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    text_input = ObjectProperty(None)


class ToolBarButton(Button):
    """ ToolBar Button """
    def buttonClicked(self, id):
        Logger.info("[%s\t] %s was clicked.", self.__class__.__name__, id)
        if id == 'Open':
            self.parent.parent.show_load()
        if id == 'Save':
            self.parent.parent.popup_save_menu()


class ToolBar(Widget):
    """ ToolBar Widget """


class RootWidget(Widget):
    """ Root Widget """
    diagram_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.painter = None
        self._popup_menu = None
        self._popup = None
        self.xml_loader = None

    def popup_save_menu(self):
        content = PopupSaveMenu(popup_close=self.popup_close_menu, show_save=self.show_save)
        self._popup_menu = Popup(title='Save', content=content, size_hint=(0.5, 0.5), auto_dismiss=False)
        self._popup_menu.open()

    def popup_close_menu(self):
        self._popup_menu.dismiss()

    def save_pptx(self, path, filename):
        pptx_saver = PPTXSaver(os.path.join(path, filename), self.painter)
        pptx_saver.save()

        self.dismiss_popup()
        self.popup_close_menu()

    def save_svg(self, path, filename):
        svg_saver = SVGSaver(os.path.join(path, filename), self.painter)
        svg_saver.save()

        self.dismiss_popup()
        self.popup_close_menu()

    def save_png(self, path, filename):
        png_saver = PNGSaver(os.path.join(path, filename), self.painter)
        png_saver.save()

        self.dismiss_popup()
        self.popup_close_menu()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Open Digaram",
                            content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self, save_type):
        if save_type == 'PowerPoint':
            content = SaveDialog(save=self.save_pptx, cancel=self.dismiss_popup)

        elif save_type == 'PNG':
            content = SaveDialog(save=self.save_png, cancel=self.dismiss_popup)

        else:
            content = SaveDialog(save=self.save_svg, cancel=self.dismiss_popup)   

        self._popup = Popup(title="Save Digaram",
                            content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.xml_loader = XMLLoader(os.path.join(path, filename[0]))
        effect = self.xml_loader.get_effect()
        Logger.info("[%s\t] Effect = %s", self.__class__.__name__, effect)
        self.diagram_view.reset()

        self.painter = DiagramPainter(self.diagram_view, self.xml_loader)
        self.painter.draw()

        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def on_touch_down(self, touch):
        touch.ud['x'] = touch.pos[0]
        touch.ud['y'] = touch.pos[1]

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):

        dx = touch.pos[0] - touch.ud['x']
        dy = - (touch.pos[1] - touch.ud['y'])

        touch.ud['x'] = touch.pos[0]
        touch.ud['y'] = touch.pos[1]

        if self.painter is not None:
            self.painter.redraw(dx, dy)

        return super().on_touch_move(touch)


class DiagramView(StencilView):
    """ Widget to display Diagram """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rect = None

    def reset(self):
        self.clear_widgets()
        self.canvas.clear()
        self.canvas.add(Color(rgb=[.9, .9, .9]))
        self.rect = Rectangle(pos=self.pos, size=self.size)
        self.canvas.add(self.rect)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, _):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MainApp(App):
    """ Main App """
    title = 'Fishbone Diagram Generator'
    icon = 'images/icon16.png'

    def build(self):
        if os.path.exists('fonts/ipaexg.ttf'):
            resource_add_path('fonts/')
            LabelBase.register(DEFAULT_FONT, 'ipaexg.ttf')

        Config.set("input", "mouse", "mouse,multitouch_on_demand")

        widget = RootWidget()

        return widget


if __name__ == '__main__':
    MainApp().run()
