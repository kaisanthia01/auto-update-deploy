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
    QLabel,
    QDialog,
    QTextEdit,
)
from PySide6.QtGui import QIcon, QColor, QBrush
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtCore import QLocale

# บังคับให้ Qt ใช้เลขอาราบิก (เช่น en_US locale)
QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))


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


class TableViewSkewT(QWidget):
    def __init__(self, tab_name="", data=None):
        super().__init__()
        self.setWindowTitle(f"Table View UpperWind - {tab_name}")
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowIcon(
            QIcon(os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico"))
        )

        self.original_data = data if data else {}
        self.headers, self.data_list = self._flatten_data(self.original_data)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.search_box = QLineEdit(placeholderText="🔍 พิมพ์คำค้นหา...")
        self.search_box.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_box)

        self._create_table_view()
        layout.addWidget(self.table_view)

        self.delete_button = QPushButton("🗑️ ลบแถวที่เลือก")
        self.delete_button.clicked.connect(self.remove_selected_row)
        layout.addWidget(self.delete_button)

        self.error_button = QPushButton("🚨 แสดง Validation Errors")
        self.error_button.clicked.connect(self.show_validation_errors)
        # layout.addWidget(self.error_button)

        self._set_style()

    def _create_table_view(self):
        self.model = JSONTableModel(self.data_list, self.headers)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setSortingEnabled(True)

        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _flatten_data(self, data_dict):
        if not data_dict:
            return [], []

        flat_data = []
        for date_str, day_block in data_dict.items():
            time_str = day_block.get("time", "")
            timestamp_str = day_block.get("timestamp", "")

            for station_id, station_block in day_block.items():
                if station_id in ["time", "timestamp"]:
                    continue

                for code_type in ["TEMP", "WIND"]:
                    level_data = station_block.get(code_type, {})
                    for pressure_level, values in level_data.items():
                        for val in values:
                            flat_data.append(
                                {
                                    "station": station_id,
                                    "date": date_str,
                                    "time": time_str,
                                    "code_type": code_type,
                                    "pressure_level": pressure_level,
                                    "temp/wind": val,
                                    "timestamp": timestamp_str,
                                }
                            )

        headers = [
            "station",
            "date",
            "time",
            "code_type",
            "pressure_level",
            "temp/wind",
            "timestamp",
        ]
        return headers, flat_data

    def filter_table(self):
        self.proxy_model.setFilterFixedString(self.search_box.text())

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

        # ✅ บันทึกลงไฟล์ JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))  # ตำแหน่งไฟล์ .py
        output_path = os.path.join(script_dir, "../data/json/synop_data_skewt.json")

        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกแถวที่ต้องการลบ!")
            return

        # ลบแถวจาก model
        for index in sorted(selected, reverse=True):
            source_index = self.proxy_model.mapToSource(index)
            row = source_index.row()
            # print(f"กำลังลบแถวที่ index = {row}")
            self.model.removeRow(row)

        # ✅ แปลง self.data_list ที่เหลือกลับเป็นโครงสร้าง JSON เดิม
        rebuilt_json = {}
        for item in self.model.data_list:
            date = item["date"]
            time = item["time"]
            timestamp = item["timestamp"]
            station = item["station"]
            code_type = item["code_type"]
            level = item["pressure_level"]
            value = item["temp/wind"]

            if date not in rebuilt_json:
                rebuilt_json[date] = {"time": time, "timestamp": timestamp}
            if station not in rebuilt_json[date]:
                rebuilt_json[date][station] = {"TEMP": {}, "WIND": {}}
            if level not in rebuilt_json[date][station][code_type]:
                rebuilt_json[date][station][code_type][level] = []

            rebuilt_json[date][station][code_type][level].append(value)

        # ✅ เขียนกลับลงไฟล์ JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "../data/json/synop_data_skewt.json")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(rebuilt_json, f, ensure_ascii=False, indent=4)
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
                errors.append(
                    f"{station}:\n  - " + "\n  - ".join(row["validation_errors"])
                )

        if not errors:
            QMessageBox.information(self, "ไม่มีข้อผิดพลาด", "ไม่พบ Validation Errors")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("รายการ Validation Errors")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)
        text_area = QTextEdit(readOnly=True)
        text_area.setText("\n\n".join(errors))
        layout.addWidget(text_area)
        dlg.exec()

    def _set_style(self):
        self.setStyleSheet(
            """
            QWidget { background-color: lightblue; }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A7C7E7, stop:1 #6A95C1);
                color: white; border-radius: 8px;
                border: 1px solid #5B7FAD; padding: 6px 14px;
                font: bold 14px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2f4f82, stop:1 #5a83c4);
            }
            QLineEdit {
                border: 1px solid #91BEE9; border-radius: 8px;
                padding: 8px; background-color: #fff;
                color: #2A3D66; font: 14px;
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
        """
        )
