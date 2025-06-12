import QtQuick 2.0

ListView {
    id: root

    // ✅ เพิ่ม property เพื่อ expose วันที่
    property date date: selectedDate

    // public
    function set(date) {
        selectedDate = new Date(date);
        date = selectedDate; // ✅ อัปเดตค่า date ด้วย
        positionViewAtIndex((selectedDate.getFullYear()) * 12 + selectedDate.getMonth(), ListView.Center);
    }

    signal clicked(date date)

    property date selectedDate: new Date()

    width: 500
    height: 150
    snapMode: ListView.SnapOneItem
    orientation: Qt.Horizontal
    clip: true

    model: 3000 * 12

    delegate: Item {
        property int year: Math.floor(index / 12)
        property int month: index % 12
        property int firstDay: new Date(year, month, 1).getDay()

        width: root.width
        height: root.height

        Column {
            Item {
                width: root.width
                height: root.height - grid.height

                Text {
                    anchors.centerIn: parent
                    text: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month] + ' ' + year
                    font.pixelSize: 14
                    font.bold: true
                    color: "#fff"
                }
            }

            Grid {
                id: grid

                width: root.width
                height: 0.875 * root.height
                property real cellWidth: width / columns
                property real cellHeight: height / rows

                columns: 7
                rows: 7

                Repeater {
                    model: grid.columns * grid.rows

                    delegate: Rectangle {
                        property int day: index - 7
                        property int date: day - firstDay + 1

                        width: grid.cellWidth
                        height: grid.cellHeight

                        // เช็คว่าใช่วันเลือกไหม
                        readonly property bool isSelected: new Date(year, month, date).toDateString() === selectedDate.toDateString() && text.text && day >= 0

                        color: isSelected ? "#2a3a5f" : "#fff"
                        border.width: isSelected ? 1 : 0
                        border.color: isSelected ? "#1b1b1b" : "transparent"
                        radius: 4
                        opacity: !mouseArea.pressed ? 1 : 0.4

                        Text {
                            id: text
                            anchors.centerIn: parent
                            font.pixelSize: 0.5 * parent.height
                            font.bold: new Date(year, month, date).toDateString() === new Date().toDateString()
                            color: isSelected ? "white" : "#333"
                            text: {
                                if (day < 0)
                                    ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][index];
                                else if (new Date(year, month, date).getMonth() === month)
                                    date;
                                else
                                    '';
                            }
                        }

                        // ✅ ตอนคลิกวันที่
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            enabled: text.text && day >= 0
                            onClicked: {
                                selectedDate = new Date(year, month, date);
                                root.date = selectedDate; // ✅ อัปเดต property date ที่เปิดให้ข้างนอก
                                root.clicked(selectedDate); // 🔔 ส่งสัญญาณออก
                            }
                        }
                    }
                }
            }
        }
    }

    // Component.onCompleted: set(new Date())
}
