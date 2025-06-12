import QtQuick 2.15
import QtQuick.Controls 6.5
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "components" // Custom DatePicker

Rectangle {
    id: root
    width: 1380
    height: 800

    property int currentIndex: 0
    property bool isFullscreen: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 6

        // ===== Top Bar with Logo and Controls =====
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 10
            spacing: 10

            RowLayout {
                spacing: 6
                Image {
                    source: "../../images/icons/logowxao-3.png"
                    width: 24; height: 24
                    fillMode: Image.PreserveAspectFit
                }
                Text {
                    text: "AWSS Weather Map"
                    font.pixelSize: 18
                    color: "#2a3a5f"
                    font.bold: true
                }
            }

            Item { Layout.fillWidth: true } // Spacer

            RowLayout {
                spacing: 8
                ToolButton {
                    icon.name: "window-minimize"
                    onClicked: root.showMinimized()
                }
                ToolButton {
                    icon.name: root.isFullscreen ? "window-restore" : "window-maximize"
                    onClicked: {
                        root.isFullscreen ? root.showNormal() : root.showFullScreen()
                        root.isFullscreen = !root.isFullscreen
                    }
                }
                ToolButton {
                    icon.name: "window-close"
                    onClicked: Qt.quit()
                }
            }
        }

        // ===== Main Content Area =====
        SplitView {
            anchors.fill: parent

            // Left Panel: Map Preview
            GroupBox {
                title: "Preview Meteorological Map"
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 4

                    TabBar {
                        id: tabBar
                        Layout.fillWidth: true
                        currentIndex: root.currentIndex
                        onCurrentIndexChanged: root.currentIndex = currentIndex

                        TabButton { text: "\uD83C\uDF0D Surface อต.ทอ. 1001" }
                        TabButton { text: "\u26A1 Pressure Change อต.ทอ. 1010" }
                        TabButton { text: "\uD83D\uDCC8 Detail อต.ทอ. 1003" }
                        TabButton { text: "\uD83D\uDCA8 Upper Wind Air - 1 อต.ทอ. 1002" }
                        TabButton { text: "\uD83D\uDCC5 Skew-T Log-P Diagram - อต.ทอ. 1011" }
                    }

                    StackLayout {
                        id: tabStack
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: root.currentIndex

                        Rectangle { color: "white"; anchors.fill: parent }
                        Rectangle { color: "#fdfdfd"; anchors.fill: parent }
                        Rectangle { color: "#fcfcfc"; anchors.fill: parent }
                        Rectangle { color: "#fbfbfb"; anchors.fill: parent }
                        Rectangle { color: "#fafafa"; anchors.fill: parent }
                    }
                }
            }

            // Right Panel: Options
            GroupBox {
                title: "General Options"
                Layout.minimumWidth: 320
                Layout.fillHeight: true

                Flickable {
                    anchors.fill: parent
                    contentHeight: column.implicitHeight
                    clip: true

                    ColumnLayout {
                        id: column
                        width: parent.width - 20
                        spacing: 10

                        Label { text: "\uD83D\uDCC5 Date:" }
                        DatePicker {
                            id: datePicker
                            Layout.fillWidth: true
                            onClicked: date => console.log("📅 Selected:", date.toDateString())
                            Component.onCompleted: set(new Date())
                        }

                        Label { text: "\uD83D\uDC50 Time:" }
                        ComboBox {
                            model: ["0000 UTC | 0700 LST", "0600 UTC | 1300 LST", "1200 UTC | 1900 LST", "1800 UTC | 2400 LST"]
                            Layout.fillWidth: true
                        }

                        Label { text: "Data Value: " + Math.round(dataSlider.value) + "%" }
                        Slider {
                            id: dataSlider
                            from: 50; to: 100; value: 70
                            Layout.fillWidth: true
                        }

                        RowLayout {
                            RadioButton { text: "🎚 Plot Begin SFC"; checked: true }
                            RadioButton { text: "🎚 Plot Begin 925mb" }
                        }

                        Button {
                            text: "🌏 Load Data"
                            Layout.fillWidth: true
                        }

                        Button {
                            text: "📊 Table Viewer"
                            enabled: false
                            Layout.fillWidth: true
                        }

                        Button {
                            text: "🗀 Plot Surface อต.ทอ. 1001"
                            enabled: false
                            Layout.fillWidth: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6
                            Button { text: "📄 Save PDF"; Layout.fillWidth: true }
                            Button { text: "📸 Save PNG"; Layout.fillWidth: true }
                        }

                        Button {
                            text: "📂 Open Text File"
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }

        // ===== Bottom: Debugger =====
        GroupBox {
            title: "CheckCode Debugger"
            Layout.fillWidth: true
            Layout.preferredHeight: 100

            TextArea {
                wrapMode: TextArea.Wrap
                readOnly: true
                text: "✅ Ready."
                font.pixelSize: 13
                padding: 8
                background: Rectangle {
                    color: "white"
                    border.color: "#aaa"
                    radius: 4
                }
            }
        }
    }
}
