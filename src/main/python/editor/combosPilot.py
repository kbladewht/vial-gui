# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGridLayout, QVBoxLayout, QLabel

from protocol.constants import VIAL_PROTOCOL_DYNAMIC
import struct
from protocol.constants import CMD_VIA_GET_PROTOCOL_VERSION

from widgets.key_widget import KeyWidget
from vial_device import VialKeyboard
from editor.basic_editor import BasicEditor
from widgets.tab_widget_keycodes import TabWidgetWithKeycodes
from PyQt5.QtWidgets import QComboBox
import logging



class ComboEntryUI(QObject):

    key_changed = pyqtSignal()
    combo_changed = pyqtSignal()

    def __init__(self, idx, usb_send=hid_send):
        super().__init__()
        # self.dev = dev
        self.usb_send = usb_send
        self.idx = idx
        self.container = QGridLayout()
        self.kc_inputs = []
        self.populate_container()

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        w.setLayout(self.container)
        l = QVBoxLayout()
        l.addWidget(w)
        l.setAlignment(w, QtCore.Qt.AlignHCenter)
        self.w2 = QWidget()
        self.w2.setLayout(l)

    def populate_container(self):
           # 添加下拉列表 (QComboBox)
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Radio Addr1", "Radio Addr2", "Radio Addr3"])  # 示例模式
        self.combo_box.currentIndexChanged.connect(self.on_combo_changed)
        self.container.addWidget(QLabel("Select Mode"), 5, 0)
        self.container.addWidget(self.combo_box, 5, 1)
       
        
    def on_combo_changed(self):
        # 获取当前选中的索引和文本
        current_index = self.combo_box.currentIndex()
        current_text = self.combo_box.currentText()
        
        # 打印日志
        logging.info(f"Selected index: {current_index}, text: {current_text}")
        
        # 发出 combo_changed 信号，并传递当前选中的索引或文本
        self.combo_changed.emit()
        # data = self.usb_send(self.device, struct.pack("B", CMD_VIA_GET_PROTOCOL_VERSION), retries=1)
    def widget(self):
        return self.w2

    def load(self, data):
        # 只加载下拉框数据，其他数据不再处理
        self.combo_box.setCurrentIndex(0)  # 假设 data[0] 是下拉框的索引

    def save(self):
        return (self.combo_box.currentIndex(),)
    def on_key_changed(self):
        self.key_changed.emit()

class CombosPilot(BasicEditor):

    def __init__(self):
        super().__init__()
        self.keyboard = None
        self.device = None
        self.combo_entries = []
        self.combo_entries_available = []
        self.tabs = TabWidgetWithKeycodes()
        for x in range(1):  # 这里只创建一个条目
            entry = ComboEntryUI(x)
            entry.key_changed.connect(self.on_key_changed)
            entry.combo_changed.connect(self.on_combo_changed)
            self.combo_entries_available.append(entry)

        self.addWidget(self.tabs)

    def rebuild_ui(self):
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        self.combo_entries = self.combo_entries_available[:self.keyboard.combo_count]
        for x, e in enumerate(self.combo_entries):
            self.tabs.addTab(e.widget(), str(x + 1))
        for x, e in enumerate(self.combo_entries):
            e.load(self.keyboard.combo_get(x))

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.rebuild_ui()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= VIAL_PROTOCOL_DYNAMIC
                and self.device.keyboard.combo_count > 0)

    def on_key_changed(self):
        for x, e in enumerate(self.combo_entries):
            self.keyboard.combo_set(x, self.combo_entries[x].save())

    def on_combo_changed(self):
        print("combo changed pilot")
        CMD_VIA_GET_PROTOCOL_VERSION = 0x01
        data = self.keyboard.usb_send(self.keyboard.dev, struct.pack("B", CMD_VIA_GET_PROTOCOL_VERSION), retries=1)
   