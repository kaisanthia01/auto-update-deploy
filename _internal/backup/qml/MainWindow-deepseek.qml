// File: ui/qml/main.qml
import QtQuick
import QtQuick.Controls 6.5
import QtQuick.Window
import QtQuick.Layouts
import "components"

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
        color: "#eaf4fc"
        radius: 8
        z: 0

        // Title Bar
        Row {
            id: titleBar
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
                text: "AWSx Weather Map"
                font.pixelSize: 16
                color: "#2a3a5f"
            }
        }

        // Window Controls
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

        // Main Content
        GridLayout {
            anchors.fill: parent
            anchors.margins: 20
            columns: 2
            columnSpacing: 20
            rowSpacing: 20
            z: 1

            // Map Preview Area (Left)
            GroupBox {
                title: "Preview Meteorological Map"
                Layout.rowSpan: 2
                Layout.column: 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.75

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8

                    TabBar {
                        id: tabBar
                        Layout.fillWidth: true
                        currentIndex: root.currentIndex
                        onCurrentIndexChanged: root.currentIndex = currentIndex

                        TabButton {
                            text: "Surface on no. 1001"
                        }
                        TabButton {
                            text: "Pressure Change on no. 1010"
                        }
                        TabButton {
                            text: "Detail on no. 1003"
                        }
                        TabButton {
                            text: "Upper Wind Air - 1 on no. 1002"
                        }
                        TabButton {
                            text: "Skew-T Log-P Diagram - no. 1011"
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

            // General Options (Right Top)
            GroupBox {
                title: "General Options"
                Layout.column: 1
                Layout.row: 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.25

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12

                    // Date Selection
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Label {
                            text: "Date:"
                            Layout.preferredWidth: 80
                        }
                        DatePicker {
                            id: datePicker
                            Layout.fillWidth: true
                            onClicked: date => {
                                console.log("Date selected:", date.toDateString());
                            }
                            Component.onCompleted: set(new Date());
                        }
                    }

                    // Time Selection
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Label {
                            text: "Time:"
                        }
                        RadioButton {
                            text: "0000 UTC | 0700"
                            checked: true
                        }
                        RadioButton {
                            text: "0600 UTC | 1300"
                        }
                        RadioButton {
                            text: "1200 UTC | 1900"
                        }
                        RadioButton {
                            text: "1800 UTC | 2400"
                        }
                    }

                    // Data Value Slider
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Label {
                            text: "Data Value: " + Math.round(dataSlider.value) + "%"
                        }
                        Slider {
                            id: dataSlider
                            Layout.fillWidth: true
                            from: 50
                            to: 100
                            value: 70
                        }
                    }

                    // Checkbox Options
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        CheckBox {
                            text: "Plot Begin SFC"
                            checked: true
                        }
                        CheckBox {
                            text: "Plot Begin"
                        }
                        CheckBox {
                            text: "Load Data"
                        }
                        CheckBox {
                            text: "Table Viewer"
                        }
                        CheckBox {
                            text: "Plot Surface on no. 1001"
                        }
                    }

                    // Action Buttons
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Button {
                            text: "Save PDF"
                            Layout.fillWidth: true
                        }
                        Button {
                            text: "Save PNG"
                            Layout.fillWidth: true
                        }
                    }

                    Button {
                        text: "Open Text File"
                        Layout.fillWidth: true
                    }
                }
            }

            // Debugger (Right Bottom)
            GroupBox {
                title: "CheckCode Debugger"
                Layout.column: 1
                Layout.row: 1
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.25

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8

                    CheckBox {
                        text: "Ready."
                        checked: true
                    }

                    TextArea {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        wrapMode: TextArea.Wrap
                        placeholderText: "Debug messages will appear here..."
                        readOnly: true
                    }
                }
            }
        }
    }
}