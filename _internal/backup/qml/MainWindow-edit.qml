// File: ui/qml/main.qml
import QtQuick
import QtQuick.Controls 6.5
import QtQuick.Window
import QtQuick.Layouts
import "components" // ถ้าคุณวางไฟล์ไว้ใน ui/qml/components/DatePicker.qml

Rectangle {
    id: root
    width: 1380
    height: 800
    radius: 8

    property int currentIndex: 0
    property string currentTab: tabBar.currentItem.text
    property bool isFullscreen: false

    Rectangle {
        anchors.fill: parent
        color: "#334a80"
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
                source: "../../images/icons/logowxao-5.png"
                width: 50
                fillMode: Image.PreserveAspectFit
            }

            Text {
                id: titleLabel
                text: "Meteorological Plotting System Map"
                font.pixelSize: 16
                color: "#fff"
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
                    onClicked: rootWindow.showMinimized()
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
                            rootWindow.showNormal();
                            root.isFullscreen = false;
                        } else {
                            rootWindow.showFullScreen();
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
                    onClicked: rootWindow.closeApp()
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
            anchors.topMargin: 35
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            anchors.bottomMargin: 10
            columns: 2
            columnSpacing: 12
            rowSpacing: 12
            z: 1

            property real leftWeight: 4
            property real rightWeight: 1

            GroupBox {
                id: previewGroup
                title: "Preview Weather Map"
                Layout.rowSpan: 2
                Layout.column: 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.8

                // ✅ ปรับแต่ง label/title
                label: Item {
                    width: parent.width * 0.2
                    height: 20
                    anchors.left: parent.left
                    anchors.leftMargin: 10

                    Rectangle {
                        anchors.fill: parent
                        color: "#e3f2fd"        // พื้นหลัง title
                        radius: 6
                        antialiasing: true
                        layer.enabled: true
                        layer.smooth: true

                        Text {
                            anchors.centerIn: parent
                            text: previewGroup.title
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2a3a5f"
                        }
                    }
                }

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    TabBar {
                        id: tabBar
                        Layout.fillWidth: true
                        currentIndex: root.currentIndex
                        onCurrentIndexChanged: root.currentIndex = currentIndex

                        TabButton {
                            text: "🗺️ Surface อต.ทอ. 1001"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#2a3a5f" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }

                            hoverEnabled: true
                            ToolTip.visible: hovered
                            ToolTip.text: text
                        }

                        TabButton {
                            text: "🗺️ Pressure Change อต.ทอ. 1010"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#2a3a5f" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }

                            hoverEnabled: true
                            ToolTip.visible: hovered
                            ToolTip.text: text
                        }
                        TabButton {
                            text: "🗺️ Detail อต.ทอ. 1003"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#2a3a5f" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }

                            hoverEnabled: true
                            ToolTip.visible: hovered
                            ToolTip.text: text
                        }
                        TabButton {
                            text: "🗺️ Upper Wind Air - 1 อต.ทอ. 1002"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#2a3a5f" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }

                            hoverEnabled: true
                            ToolTip.visible: hovered
                            ToolTip.text: text
                        }
                        TabButton {
                            text: "📈 Skew-T Log-P Diagram - อต.ทอ. 1011"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#2a3a5f" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }

                            hoverEnabled: true
                            ToolTip.visible: hovered
                            ToolTip.text: text
                        }
                    }

                    StackLayout {
                        id: tabStack
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: root.currentIndex

                        Rectangle {
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                        }
                        Rectangle {
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                        }
                        Rectangle {
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                        }
                        Rectangle {
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                        }
                        Rectangle {
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                        }
                    }
                }
            }

            GroupBox {
                id: generalOptions
                title: "General Options"
                Layout.column: 1
                Layout.row: 0
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width * 0.2

                // ✅ ปรับแต่ง label/title
                label: Item {
                    width: parent.width * 0.5
                    height: 20
                    anchors.left: parent.left
                    anchors.leftMargin: 10

                    Rectangle {
                        anchors.fill: parent
                        color: "#e3f2fd"        // พื้นหลัง title
                        radius: 6
                        antialiasing: true
                        layer.enabled: true
                        layer.smooth: true

                        Text {
                            anchors.centerIn: parent
                            text: generalOptions.title
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2a3a5f"
                        }
                    }
                }

                GridLayout {
                    id: optionsLayout
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 10
                    anchors.fill: parent

                    DatePicker {
                        id: datePicker
                        Layout.fillWidth: true
                        Layout.columnSpan: 2
                        onClicked: date => console.log("📅 Date selected:", date.toDateString())
                        Component.onCompleted: set(new Date())
                    }

                    // 🧭 Time Combo
                    Label {
                        text: "🧭 Time:"
                        Layout.alignment: Qt.AlignRight
                    }
                    ComboBox {
                        Layout.fillWidth: true
                        model: ["0000 UTC | 0700 LST", "0600 UTC | 1300 LST", "1200 UTC | 1900 LST", "1800 UTC | 2400 LST"]
                    }

                    // 📊 Data Slider
                    Label {
                        text: "Data Value: " + Math.round(dataSlider.value) + "%"
                        Layout.alignment: Qt.AlignRight
                    }
                    Slider {
                        id: dataSlider
                        from: 50
                        to: 100
                        value: 70
                        Layout.fillWidth: true
                    }

                    // 🎚️ Radio Button Pair
                    Label {
                        text: "🎚 Pressure Level:"
                        Layout.alignment: Qt.AlignRight
                    }
                    RowLayout {
                        spacing: 10
                        RadioButton {
                            id: sfcRadio
                            text: "SFC"
                            checked: true
                        }
                        RadioButton {
                            text: "925mb"
                        }
                    }

                    // 🌏 Load Data Button + 📊 Table Viewer
                    RowLayout {
                        Layout.columnSpan: 2
                        spacing: 10

                        // 🌏 Load Data Button
                        Button {
                            text: "🌏 Load Data"
                            Layout.fillWidth: true
                            ToolTip.text: "โหลดข้อมูล"
                        }

                        // 📊 Table Viewer
                        Button {
                            text: "📊 Table Viewer"
                            enabled: false
                            Layout.fillWidth: true
                        }
                    }

                    // 🌏 Load Data Button
                    Button {
                        text: "🌏 Load Data"
                        Layout.columnSpan: 2
                        Layout.fillWidth: true
                        ToolTip.text: "โหลดข้อมูล"
                    }

                    // 📊 Table Viewer
                    Button {
                        text: "📊 Table Viewer"
                        enabled: false
                        Layout.columnSpan: 2
                        Layout.fillWidth: true
                    }

                    // 🗀 Plot Surface
                    Button {
                        text: "🗀 Plot Surface อต.ทอ. 1001"
                        ToolTip.text: "สร้างแผนที่ผิวพื้น SYNOP"
                        enabled: false
                        Layout.columnSpan: 2
                        Layout.fillWidth: true
                    }

                    // 📄 Save PDF + PNG
                    RowLayout {
                        Layout.columnSpan: 2
                        spacing: 10
                        Button {
                            text: "📄 Save PDF"
                            Layout.fillWidth: true
                        }
                        Button {
                            text: "📸 Save PNG"
                            Layout.fillWidth: true
                        }
                    }

                    // 📂 Open File
                    Button {
                        text: "📂 Open Text File"
                        Layout.columnSpan: 2
                        Layout.fillWidth: true
                    }
                }
            }

            GroupBox {
                id: checkCodeDebugger
                title: "CheckCode Debugger"
                Layout.column: 1
                Layout.row: 1
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.2

                // ✅ ปรับแต่ง label/title
                label: Item {
                    width: parent.width * 0.6
                    height: 20
                    anchors.left: parent.left
                    anchors.leftMargin: 10

                    Rectangle {
                        anchors.fill: parent
                        color: "#e3f2fd"        // พื้นหลัง title
                        radius: 6
                        antialiasing: true
                        layer.enabled: true
                        layer.smooth: true

                        Text {
                            anchors.centerIn: parent
                            text: checkCodeDebugger.title
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2a3a5f"
                        }
                    }
                }

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
