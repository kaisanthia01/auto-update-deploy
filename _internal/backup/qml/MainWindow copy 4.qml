// File: ui/qml/main.qml
import QtQuick
import QtQuick.Controls 6.5
import QtQuick.Window
import QtQuick.Layouts
import "components" // ถ้าคุณวางไฟล์ไว้ใน ui/qml/components/DatePicker.qml

Rectangle {
    id: root
    width: 1470
    height: 800
    radius: 8

    property int currentIndex: 0
    property string currentTab: tabBar.currentItem.text
    property bool isFullscreen: false
    property string debugText: ""
    property string surfaceImagePath: Qt.applicationDirPath + "/images/map/surface.png"
    property string pressureImagePath: "file://" + Qt.applicationDirPath + "/images/map/pressure.png"
    property string detailImagePath: "file://" + Qt.applicationDirPath + "/images/map/detail.png"
    property string upperwind1ImagePath: "file://" + Qt.applicationDirPath + "/images/map/upperwind1.png"
    property string upperwind2ImagePath: "file://" + Qt.applicationDirPath + "/images/map/upperwind2.png"
    property string skewtImagePath: "file://" + Qt.applicationDirPath + "/images/map/skewt.png"

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
                            color: "#1b2a4b"
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
                            id: surfaceTab
                            text: "🗺️ Surface อต.ทอ. 1001"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#1b2a4b" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }
                        }

                        TabButton {
                            id: pressureTab
                            text: "🗺️ Pressure Change อต.ทอ. 1010"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#1b2a4b" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }
                        }
                        TabButton {
                            id: detailTab
                            text: "🗺️ Detail อต.ทอ. 1003"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#1b2a4b" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }
                        }
                        TabButton {
                            id: wind1Tab
                            text: "🗺️ Upper Wind Air - 1 อต.ทอ. 1002"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#1b2a4b" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }
                        }
                        TabButton {
                            id: wind2Tab
                            text: "🗺️ Upper Wind Air - 2 อต.ทอ. 1013"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#1b2a4b" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }
                        }
                        TabButton {
                            id: skewtTab
                            text: "📈 Skew-T Log-P - อต.ทอ. 1011"
                            padding: 8

                            contentItem: Text {
                                text: parent.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                font.pixelSize: parent.checked ? 12 : 10
                                font.bold: parent.checked
                                color: parent.checked ? "#1b2a4b" : "#555"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: parent.checked ? "#e3f2fd" : "#ffffff"
                                topLeftRadius: 8
                                topRightRadius: 8
                                antialiasing: true
                            }
                        }
                    }

                    StackLayout {
                        id: tabStack
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: root.currentIndex

                        Rectangle {
                            id: surfaceView
                            color: "#e3f2fd"
                            anchors.fill: parent
                            radius: 8
                            clip: true

                            property real zoom: 1.0
                            property point offset: Qt.point(0, 0)   // ตำแหน่งเลื่อน
                            property point zoomCenter: Qt.point(width / 2, height / 2)
                            property bool isDragging: false

                            Image {
                                id: zoomableImage
                                source: "../../images/map/surface.png"
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                                asynchronous: true
                                cache: false

                                transform: [
                                    Translate {
                                        x: surfaceView.offset.x
                                        y: surfaceView.offset.y
                                    },
                                    Scale {
                                        origin.x: surfaceView.zoomCenter.x
                                        origin.y: surfaceView.zoomCenter.y
                                        xScale: surfaceView.zoom
                                        yScale: surfaceView.zoom
                                    }
                                ]
                            }

                            MouseArea {
                                id: mouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point lastPos
                                property real startZoom: 1.0

                                onPressed: {
                                    lastPos = Qt.point(mouse.x, mouse.y);
                                    startZoom = surfaceView.zoom;
                                    isDragging = true;
                                    cursorShape = Qt.ClosedHandCursor;
                                }

                                onReleased: {
                                    isDragging = false;
                                    cursorShape = Qt.ArrowCursor;
                                }

                                onPositionChanged: {
                                    surfaceView.zoomCenter = Qt.point(mouse.x, mouse.y);

                                    if (pressed && (mouse.buttons & Qt.LeftButton)) {
                                        const dx = mouse.x - lastPos.x;
                                        const dy = mouse.y - lastPos.y;
                                        surfaceView.offset.x += dx;
                                        surfaceView.offset.y += dy;
                                        lastPos = Qt.point(mouse.x, mouse.y);
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = surfaceView.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.9;
                                    const newZoom = Math.max(0.2, Math.min(oldZoom * zoomFactor, 5.0));

                                    // คำนวณตำแหน่งเมาส์สัมพันธ์กับรูปภาพก่อนการซูม
                                    const imagePos = Qt.point((wheel.x - surfaceView.offset.x) / oldZoom, (wheel.y - surfaceView.offset.y) / oldZoom);

                                    // คำนวณ offset ใหม่เพื่อให้จุดที่เมาส์ชี้อยู่คงที่
                                    surfaceView.offset.x = wheel.x - imagePos.x * newZoom;
                                    surfaceView.offset.y = wheel.y - imagePos.y * newZoom;

                                    surfaceView.zoom = newZoom;
                                    surfaceView.zoomCenter = Qt.point(wheel.x, wheel.y);
                                }
                            }

                            // เพิ่มการแสดงค่าซูมสำหรับ debug (สามารถลบออกได้)
                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                text: `Zoom: ${surfaceView.zoom.toFixed(2)} | Offset: (${surfaceView.offset.x.toFixed(0)}, ${surfaceView.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true // ตั้งค่าเป็น true เพื่อดูค่าสถานะ
                            }
                        }

                        Rectangle {
                            id: pressureView
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                            clip: true  // ❗ จำกัดขอบภาพให้อยู่ใน rectangle

                            // ✅ ตัวแปรเก็บ scale ปัจจุบัน
                            property real zoom: 1.0

                            Image {
                                id: zoomable1Image
                                source: "../../images/map/surface.png"
                                anchors.centerIn: parent
                                fillMode: Image.PreserveAspectFit

                                // ✅ Apply scaling
                                transform: Scale {
                                    origin.x: zoomable1Image.width / 2
                                    origin.y: zoomable1Image.height / 2
                                    xScale: pressureView.zoom
                                    yScale: pressureView.zoom
                                }
                            }

                            WheelHandler {
                                id: wheel1Zoom
                                target: null  // ✅ ใช้ target: null เพื่อให้ handler ใช้ parent
                                onWheel: event => {
                                    const step = event.angleDelta.y > 0 ? 0.1 : -0.1;
                                    pressureView.zoom = Math.max(0.2, Math.min(pressureView.zoom + step, 5.0));  // จำกัด scale
                                    event.accepted = true;
                                }
                            }
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
                            color: "#1b2a4b"
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
                        text: "🕖 Time:"
                        color: "#fff"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }

                    ComboBox {
                        id: timeSelector
                        Layout.fillWidth: true
                        font.pixelSize: 10
                        model: ["0000 UTC | 0700 LST", "0600 UTC | 1300 LST", "1200 UTC | 1900 LST", "1800 UTC | 2400 LST"]
                        currentIndex: 0

                        delegate: ItemDelegate {
                            width: parent.width
                            contentItem: Text {
                                text: modelData
                                font.pixelSize: 10
                                color: "#1b2a4b"
                                elide: Text.ElideRight
                            }

                            background: Rectangle {
                                color: highlighted ? "#e3f2fd" : "white"
                            }

                            highlighted: timeSelector.highlightedIndex === index
                        }

                        contentItem: Text {
                            leftPadding: 5
                            text: timeSelector.displayText
                            font.pixelSize: 10
                            color: "#1b2a4b"
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }

                        indicator: Canvas {
                            id: indicator
                            width: 18
                            height: 18
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter

                            onPaint: {
                                var ctx = getContext("2d");
                                ctx.clearRect(0, 0, width, height);
                                ctx.beginPath();
                                ctx.moveTo(4, 6);
                                ctx.lineTo(14, 6);
                                ctx.lineTo(9, 12);
                                ctx.closePath();
                                ctx.fillStyle = "#666";
                                ctx.fill();
                            }
                        }

                        background: Rectangle {
                            radius: 6
                            color: "white"
                            border.color: "#90caf9"
                            border.width: 1
                        }
                    }

                    // 📊 Data Slider
                    Label {
                        text: "🧭 Value: " + Math.round(dataSlider.value) + "%"
                        color: "#fff"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }

                    Slider {
                        id: dataSlider
                        from: 50
                        to: 100
                        value: 70
                        Layout.fillWidth: true
                        stepSize: 1

                        background: Rectangle {
                            x: dataSlider.leftPadding
                            y: dataSlider.topPadding + dataSlider.availableHeight / 2 - height / 2
                            implicitWidth: 200
                            implicitHeight: 4
                            width: dataSlider.availableWidth
                            height: implicitHeight
                            radius: 2
                            color: "#bdbebf"

                            Rectangle {
                                width: dataSlider.visualPosition * parent.width
                                height: parent.height
                                color: "#1b2a4b"
                                radius: 2
                            }
                        }

                        handle: Rectangle {
                            x: dataSlider.leftPadding + dataSlider.visualPosition * (dataSlider.availableWidth - width)
                            y: dataSlider.topPadding + dataSlider.availableHeight / 2 - height / 2
                            implicitWidth: 15
                            implicitHeight: 15
                            radius: 13
                            color: dataSlider.pressed ? "#f0f0f0" : "#f6f6f6"
                            border.color: "#bdbebf"
                        }
                    }

                    // 🎚️ Radio Button Pair
                    Label {
                        text: "🎚 Pressure Level:"
                        color: "#fff"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                    }
                    RowLayout {
                        spacing: 16
                        RadioButton {
                            id: sfcRadio
                            text: "SFC"
                            Layout.fillWidth: true
                            checked: true

                            contentItem: Text {
                                text: sfcRadio.text
                                font.pixelSize: 14
                                color: "#fff"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 20
                            }
                        }
                        RadioButton {
                            id: mb925Radio
                            text: "925mb"
                            Layout.fillWidth: true

                            contentItem: Text {
                                text: mb925Radio.text
                                font.pixelSize: 14
                                color: "#fff"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 20
                            }
                        }
                    }

                    // 🌏 Load Data + 📊 Table Viewer
                    RowLayout {
                        Layout.columnSpan: 2
                        spacing: 10

                        // 🌏 Load Data
                        Control {
                            id: loadButton
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            implicitHeight: 30

                            background: Rectangle {
                                color: loadButton.hovered ? "#d1d1d1" : "#fff"  // สี hover
                                radius: 6
                            }

                            contentItem: Label {
                                text: "🌏 Load Data"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.bold: true
                                font.pixelSize: 14
                                color: "#1b2a4b"
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onEntered: loadButton.hovered = true
                                onExited: loadButton.hovered = false
                                onClicked: rootWindow.buttonClicked("load")
                            }
                        }

                        // 📊 Table Viewer
                        Control {
                            id: tableButton
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            implicitHeight: 30

                            background: Rectangle {
                                color: tableButton.hovered ? "#d1d1d1" : "#fff"  // สี hover
                                radius: 6
                            }

                            contentItem: Label {
                                text: "📊 Table Viewer"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.bold: true
                                font.pixelSize: 14
                                color: "#1b2a4b"
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onEntered: tableButton.hovered = true
                                onExited: tableButton.hovered = false
                                onClicked: rootWindow.buttonClicked("table")
                            }
                        }
                    }

                    // ✍ Plot
                    Control {
                        id: plotButton
                        Layout.fillWidth: true
                        Layout.columnSpan: 2
                        implicitHeight: 30

                        background: Rectangle {
                            color: plotButton.hovered ? "#d1d1d1" : "#fff"
                            radius: 6
                        }

                        contentItem: Label {
                            text: tabBar.currentItem.text
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.bold: true
                            font.pixelSize: 14
                            color: "#1b2a4b"
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onEntered: plotButton.hovered = true
                            onExited: plotButton.hovered = false
                            onClicked: rootWindow.buttonClicked("plot:" + tabBar.currentItem.text)
                        }
                    }

                    // 📄 Save PDF + 📸 Save PNG
                    RowLayout {
                        Layout.columnSpan: 2
                        spacing: 10

                        // 📄 Save PDF
                        Control {
                            id: pdfButton
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            implicitHeight: 30

                            background: Rectangle {
                                color: pdfButton.hovered ? "#318b00" : "#599d34"  // สี hover
                                radius: 6
                            }

                            contentItem: Label {
                                text: "📄 Save PDF"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.bold: true
                                font.pixelSize: 14
                                color: "black"
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onEntered: pdfButton.hovered = true
                                onExited: pdfButton.hovered = false
                                onClicked: rootWindow.buttonClicked("pdf")
                            }
                        }

                        // 📸 Save PNG
                        Control {
                            id: pngButton
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            implicitHeight: 30

                            background: Rectangle {
                                color: pngButton.hovered ? "#d39b00" : "#f5bd24"  // สี hover
                                radius: 6
                            }

                            contentItem: Label {
                                text: "📸 Save PNG"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.bold: true
                                font.pixelSize: 14
                                color: "black"
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onEntered: pngButton.hovered = true
                                onExited: pngButton.hovered = false
                                onClicked: rootWindow.buttonClicked("png")
                            }
                        }
                    }

                    // 📂 Open File
                    Control {
                        id: openButton
                        Layout.fillWidth: true
                        Layout.columnSpan: 2
                        implicitHeight: 30

                        background: Rectangle {
                            color: openButton.hovered ? "#d84339" : "#F45D4C"  // สี hover
                            radius: 6
                        }

                        contentItem: Label {
                            text: "📂 Open Text File"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.bold: true
                            font.pixelSize: 14
                            color: "white"
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onEntered: openButton.hovered = true
                            onExited: openButton.hovered = false
                            onClicked: rootWindow.buttonClicked("open")
                        }
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
                            color: "#1b2a4b"
                        }
                    }
                }

                TextArea {
                    id: debugTextArea
                    text: root.debugText
                    readOnly: true
                }
            }
        }
    }
}
