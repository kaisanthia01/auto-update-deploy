// File: ui/qml/main.qml
import QtQuick
import QtQuick.Controls 6.5
import QtQuick.Window
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1380
    height: 800
    visible: true
    title: "AWSS Weather Map"

    property int currentIndex: 0
    property string currentTab: tabBar.currentItem.text
    property bool isFullscreen: false

    Rectangle {
        anchors.fill: parent
        color: "#eaf4fc"
        radius: 8
        z: 0

        Row {
            id: iconsWindow
            spacing: 8
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 10
            z: 2

            Image {
                source: "../../images/icons/logowxao-3.png"
                width: 20
                height: 20
                fillMode: Image.PreserveAspectFit
            }

            Text {
                id: titleLabel
                text: "AWSS Weather Map"
                font.pixelSize: 16
                color: "#2a3a5f"
            }
        }

        Row {
            id: windowControls
            spacing: 8
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 10
            z: 2

            Rectangle {
                width: 14
                height: 14
                radius: 7
                color: "#ffbd2e"
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.showMinimized()
                    ToolTip.visible: hovered
                    ToolTip.delay: 300
                    ToolTip.text: "Minimize Window"
                }
                Text {
                    anchors.centerIn: parent
                    font.pixelSize: 8
                    color: "white"
                    text: "⏷"
                }
            }

            Rectangle {
                width: 14
                height: 14
                radius: 7
                color: "#27c93f"
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (root.isFullscreen) {
                            root.showNormal();
                            root.isFullscreen = false;
                        } else {
                            root.showFullScreen();
                            root.isFullscreen = true;
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.delay: 300
                    ToolTip.text: root.isFullscreen ? "Restore Window" : "Maximize Window"
                }
                Text {
                    anchors.centerIn: parent
                    font.pixelSize: 8
                    color: "white"
                    text: root.isFullscreen ? "🗗" : "🗖"
                }
            }

            Rectangle {
                width: 14
                height: 14
                radius: 7
                color: "#ff5f56"
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Qt.quit()
                    ToolTip.visible: hovered
                    ToolTip.delay: 300
                    ToolTip.text: "Close Window"
                }
                Text {
                    anchors.centerIn: parent
                    font.pixelSize: 8
                    color: "white"
                    text: "🗙"
                }
            }
        }

        GridLayout {
            anchors.fill: parent
            anchors.margins: 20
            columns: 2
            columnSpacing: 12
            rowSpacing: 12
            z: 1

            property real leftWeight: 4
            property real rightWeight: 1

            GroupBox {
                title: "Preview Meteorological Map"
                Layout.rowSpan: 2
                Layout.column: 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.8

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 4

                    TabBar {
                        id: tabBar
                        Layout.fillWidth: true
                        currentIndex: root.currentIndex
                        onCurrentIndexChanged: root.currentIndex = currentIndex

                        TabButton {
                            text: "Surface อต.ทอ. 1001"
                        }
                        TabButton {
                            text: "Pressure Change อต.ทอ. 1010"
                        }
                        TabButton {
                            text: "Detail อต.ทอ. 1003"
                        }
                        TabButton {
                            text: "Upper Wind Air - 1 อต.ทอ. 1002"
                        }
                        TabButton {
                            text: "Skew-T Log-P Diagram - อต.ทอ. 1011"
                        }
                    }

                    StackLayout {
                        id: tabStack
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: root.currentIndex

                        Rectangle {
                            color: "white"
                            anchors.fill: parent
                        }
                        Rectangle {
                            color: "#fdfdfd"
                            anchors.fill: parent
                        }
                        Rectangle {
                            color: "#fcfcfc"
                            anchors.fill: parent
                        }
                        Rectangle {
                            color: "#fbfbfb"
                            anchors.fill: parent
                        }
                        Rectangle {
                            color: "#fafafa"
                            anchors.fill: parent
                        }
                    }
                }
            }

            GroupBox {
                title: "General Options"
                Layout.column: 1
                Layout.row: 0
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width * 0.2

                GridLayout {
                    columns: 2
                    columnSpacing: 8
                    rowSpacing: 6
                    anchors.fill: parent

                    Label {
                        text: "📅 Date:"
                    }
                    Calendar {
                        id: picker
                        selectedDate: new Date()
                        onSelectedDateChanged: console.log("📅 Selected:", selectedDate)
                        width: 280
                        height: 240
                    }

                    Label {
                        text: "🖐 Time:"
                    }
                    ComboBox {
                        model: ["0000 UTC | 0700 LST", "0600 UTC | 1300 LST", "1200 UTC | 1900 LST", "1800 UTC | 2400 LST"]
                    }

                    Label {
                        text: "Data Value: " + Math.round(dataSlider.value) + "%"
                    }
                    Slider {
                        id: dataSlider
                        from: 50
                        to: 100
                        value: 70
                    }

                    RadioButton {
                        id: sfcRadio
                        text: "🎚 Plot Begin SFC"
                        checked: true
                    }
                    RadioButton {
                        text: "🎚 Plot Begin 925mb"
                    }

                    Button {
                        text: "🌏 Load Data"
                        ToolTip.text: "โหลดข้อมูล"
                        Layout.columnSpan: 2
                    }

                    Button {
                        text: "📊 Table Viewer"
                        ToolTip.text: "เปิดดูข้อมูลในรูปแบบตาราง"
                        enabled: false
                        Layout.columnSpan: 2
                        background: Rectangle {
                            radius: 8
                            color: closeControl.hovered ? "#cc0000" : "#ff4444"
                            border.width: 0
                            layer.enabled: false
                        }
                    }

                    Button {
                        text: "🗀 Plot Surface อต.ทอ. 1001"
                        ToolTip.text: "สร้างแผนที่ผิวพื้น SYNOP"
                        enabled: false
                        Layout.columnSpan: 2
                    }

                    RowLayout {
                        Layout.columnSpan: 2
                        spacing: 10
                        Button {
                            text: "📄 Save PDF"
                            ToolTip.text: "บันทึกแผนที่เป็น PDF"
                        }
                        Button {
                            text: "📸 Save PNG"
                            ToolTip.text: "บันทึกแผนที่เป็นภาพ PNG"
                        }
                    }

                    Button {
                        text: "📂 Open Text File"
                        ToolTip.text: "เปิดไฟล์ข้อความจากโฟลเดอร์ที่เลือก"
                        Layout.columnSpan: 2
                    }
                }
            }

            GroupBox {
                title: "CheckCode Debugger"
                Layout.column: 1
                Layout.row: 1
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.2

                TextArea {
                    wrapMode: TextArea.Wrap
                    placeholderText: "CheckCode Debugger"
                    readOnly: true
                    anchors.fill: parent
                    text: "✅ Ready."
                }
            }
        }
    }
}
