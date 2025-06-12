import json
import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableView,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QHeaderView,
    QDialog,
    QTextEdit,
)
from PySide6.QtGui import QIcon, QColor, QBrush
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel

import logging

logger = logging.getLogger("MainWindow")


class JSONTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self.data_list = data
        self.headers = headers
        self.validation_errors = self._build_error_lookup()

    def _build_error_lookup(self):
        error_map = {}
        for row_index, item in enumerate(self.data_list):
            for err in item.get("validation_errors", []):
                if ":" in err and "=" in err:
                    section_key, _ = err.split("=", 1)
                    error_map[(row_index, section_key.strip())] = True
        return error_map

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        key = self.headers[col]

        if role == Qt.ItemDataRole.DisplayRole:
            return self.data_list[row].get(key, "")

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.BackgroundRole:
            if (row, key) in self.validation_errors:
                return QBrush(QColor("#ffcccc"))

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            header = self.headers[section]
            return header.replace("main:", "") if header.startswith("main:") else header
        return None

    def removeRow(self, row, parent=QModelIndex()):
        if 0 <= row < len(self.data_list):
            self.beginRemoveRows(parent, row, row)
            del self.data_list[row]
            self.endRemoveRows()
            return True
        return False


class TableViewSynoptic(QWidget):
    def __init__(self, tab_name="", data=None):
        super().__init__()

        try:
            self.setWindowTitle(f"Table View Synoptic - {tab_name}")
            self.setWindowIcon(
                QIcon(
                    os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico")
                )
            )
            self.setGeometry(100, 100, 1200, 700)

            self.original_data = data if data else []
            self.headers, self.data_list = self._flatten_data(self.original_data)

            layout = QVBoxLayout()
            self.setLayout(layout)

            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("🔍 พิมพ์คำค้นหา...")
            self.search_box.textChanged.connect(self.filter_table)
            layout.addWidget(self.search_box)

            self.model = JSONTableModel(self.data_list, self.headers)
            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setSourceModel(self.model)
            self.proxy_model.setFilterCaseSensitivity(
                Qt.CaseSensitivity.CaseInsensitive
            )
            self.proxy_model.setFilterKeyColumn(-1)

            self.table_view = QTableView()
            self.table_view.setModel(self.proxy_model)
            self.table_view.setSelectionBehavior(
                QTableView.SelectionBehavior.SelectRows
            )
            self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.table_view.setSortingEnabled(True)

            header = self.table_view.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            layout.addWidget(self.table_view)

            self.delete_button = QPushButton("🗑️ ลบแถวที่เลือก")
            self.delete_button.clicked.connect(self.remove_selected_row)
            layout.addWidget(self.delete_button)

            self.error_button = QPushButton("🚨 แสดง Validation Errors")
            self.error_button.clicked.connect(self.show_validation_errors)
            layout.addWidget(self.error_button)

            self._set_style()
            self.tabName = tab_name

        except Exception as e:
            QMessageBox.critical(self, "Error", f"ไม่สามารถเปิดตารางได้:\n{e}")

    def _flatten_data(self, data_list):
        if not data_list:
            return [], []

        main_order = [
            "IrIxhVV",
            "Nddff",
            "1SnTTT",
            "2SnTdTdTd",
            "3P0P0P0",
            "4PPPP",
            "5appp",
            "6RRRtr",
            "7wwW1W2",
            "8NhClCmCH",
            "9GGgg",
        ]

        flat_data = []
        include_date = any("date" in item for item in data_list)

        for item in data_list:
            flat_row = {
                "station_id": item.get("station_id", ""),
                "validation_errors": ", ".join(item.get("validation_errors", [])),
            }
            if include_date:
                flat_row["date"] = item.get("date", "")
            if "main" in item and isinstance(item["main"], dict):
                for key in main_order:
                    flat_row[f"main:{key}"] = item["main"].get(key, "")
            flat_data.append(flat_row)

        headers = ["station_id"]
        if include_date:
            headers.append("date")
        headers += [f"main:{k}" for k in main_order] + ["validation_errors"]

        return headers, flat_data

    def filter_table(self):
        search_text = self.search_box.text()
        self.proxy_model.setFilterFixedString(search_text)

    def remove_selected_row(self):
        # selected = self.table_view.selectionModel().selectedRows()
        # if not selected:
        #    QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกแถวที่ต้องการลบ!")
        #    return
        #
        # for index in sorted(selected, reverse=True):
        #    source_row = self.proxy_model.mapToSource(index).row()
        #    self.model.removeRow(source_row)
        #
        # QMessageBox.information(self, "สำเร็จ", "ลบแถวที่เลือกเรียบร้อยแล้ว!")

        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกแถวที่ต้องการลบ!")
            return

        deleted_station_ids = set()
        deleted_dates = set()

        # เก็บ station_id กับ date ที่ต้องลบจากแถวที่เลือก
        for index in sorted(selected, reverse=True):
            source_index = self.proxy_model.mapToSource(index)
            row = source_index.row()
            row_data = self.model.data_list[row]
            station_id = row_data.get("station_id")
            date = row_data.get("date")
            if station_id:
                deleted_station_ids.add(station_id)
            if date:
                deleted_dates.add(date)
            self.model.removeRow(row)

        # กรอง original_data โดยลบรายการที่ station_id และ date ตรงกับที่เลือก
        new_data = []
        for item in self.original_data:
            sid = item.get("station_id")
            dt = item.get("date")
            # ถ้า station_id และ date ตรงกับที่จะลบ ข้ามรายการนั้น
            if sid in deleted_station_ids and dt in deleted_dates:
                continue
            new_data.append(item)

        self.original_data = new_data

        # บันทึกกลับไฟล์ JSON
        if self.tabName == "Surface อต.ทอ. 1001":
            output_path = os.path.join(
                os.path.dirname(__file__), "../data/json/synop_data_surface.json"
            )
        elif self.tabName == "Pressure Change อต.ทอ. 1010":
            output_path = os.path.join(
                os.path.dirname(__file__), "../data/json/synop_data_pressure.json"
            )
        else:
            output_path = os.path.join(
                os.path.dirname(__file__), "../data/json/synop_data_detail.json"
            )

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.original_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(
                self, "ข้อผิดพลาด", f"ไม่สามารถเขียนไฟล์ JSON ได้:\n{str(e)}"
            )
            return

        QMessageBox.information(self, "สำเร็จ", "ลบแถวที่เลือกและอัปเดตไฟล์เรียบร้อยแล้ว!")

    def show_validation_errors(self):
        errors = []
        for row in self.original_data:
            if row.get("validation_errors"):
                station = row.get("station_id", "(ไม่มีรหัสสถานี)")
                lines = [f"{station}:\n  - " + "\n  - ".join(row["validation_errors"])]
                errors.extend(lines)

        if not errors:
            QMessageBox.information(self, "ไม่มีข้อผิดพลาด", "ไม่พบ Validation Errors")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("รายการ Validation Errors")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setText("\n\n".join(errors))
        layout.addWidget(text_area)
        dlg.exec()

    def _set_style(self):
        self.setStyleSheet(
            """*
                QWidget { background-color: lightblue; }
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A7C7E7, stop:1 #6A95C1);
                    color: white;
                    border-radius: 8px;
                    border: 1px solid #5B7FAD;
                    padding: 6px 14px;
                    font: bold 14px;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2f4f82, stop:1 #5a83c4);
                }
                QLineEdit {
                    border: 1px solid #91BEE9;
                    border-radius: 8px;
                    padding: 8px;
                    background-color: #fff;
                    color: #2A3D66;
                    font: 14px;
                }
                QMessageBox, QLabel,QTextEdit {
                    background-color: #fff;
                    color: #2A3D66;
                    font: 14px;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background: #aaa;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #888;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #f0f0f0;
                    height: 10px;
                }
                QScrollBar::handle:horizontal {
                    background: #aaa;
                    min-width: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #888;
                }
            """
        )

        self.table_view.setStyleSheet(
            """
                QTableView {
                    border: 1px solid #ccc;
                    gridline-color: #ddd;
                    font-size: 14px;
                    selection-background-color: #cce5ff;
                    selection-color: #000;
                    background-color: #fff;
                }
                QHeaderView::section {
                    background-color: #f2f2f2;
                    padding: 4px;
                    border: 1px solid #ddd;
                    font-weight: bold;
                    font-size: 14px;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 10px;
                }
                QScrollBar::handle:vertical {
                    background: #aaa;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #888;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #f0f0f0;
                    height: 10px;
                }
                QScrollBar::handle:horizontal {
                    background: #aaa;
                    min-width: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #888;
                }
            """
        )
