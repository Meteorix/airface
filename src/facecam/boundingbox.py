# coding=utf-8
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout


Builder.load_string('''

#:set line_width dp(2)
#:set label_height dp(18.0)

<BoundingBox>:
    label: name_label
    
    canvas:
        Color:
            rgba: root.border_color

        Line:
            width: line_width
            rectangle: [root.pos[0], root.pos[1]-label_height, root.width, root.height+label_height]
            cap: "round"

        Rectangle:
            pos: root.pos[0], root.pos[1]-label_height
            size: root.width, label_height

    canvas.before:
        Rotate:
            angle: root.rotate_angle
            origin: root.rotate_center
    Label:
        id: name_label
        size_hint: None, None
        pos: root.pos[0], root.pos[1]-label_height
        size: root.width, label_height
        text_size: self.size
        color: 1, 1, 1, 1
        halign: "center"
        valign: "middle"
        font_size: "15dp"
        bold: True
        text: root.name
''')


class BoundingBox(FloatLayout):
    """
    BoundingBox class which is drawn around a face.
    """

    rotate_angle = NumericProperty(0)

    rotate_center = ListProperty((0, 0))

    border_color = ListProperty((1, 0, 0, 1))
    '''
    Color of the bounding box around a face.
    '''

    label = ObjectProperty(None)
    '''
    Text color of the label which displays the name of a person.
    '''

    name = StringProperty("Unknown")
    '''
    Name of the identified Person.
    '''
