"""
XML reading module
"""
import xml.etree.ElementTree as ET


class XMLLoader():
    """ XML reading class """
    def __init__(self, filepath):
        with open(filepath, encoding='shift_jis') as file:
            xml = file.read()
        self.root = ET.fromstring(xml)

    def get_diagram_param(self, param):
        return self.root.attrib[param]

    def get_effect(self):
        return self.root.find('Effect').text

    def get_factor(self):
        return self.root.findall('Factor')
