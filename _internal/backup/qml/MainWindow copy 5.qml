// File: ui/qml/main.qml
import QtQuick
import QtQuick.Controls 6.5
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Dialogs
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
    property string surfaceImageMapPath: Qt.resolvedUrl("file:./images/map/surface.png")
    property string pressureImageMapPath: Qt.resolvedUrl("file:./images/map/pressure.png")
    property string detailImageMapPath: Qt.resolvedUrl("file:./images/map/detail.png")
    property string upperwind1ImageMapPath: Qt.resolvedUrl("file:./images/map/upperwind1.png")
    property string upperwind2ImageMapPath: Qt.resolvedUrl("file:./images/map/upperwind2.png")
    property string skewtImageMapPath: Qt.resolvedUrl("file:./images/map/skewt.png")

    property string surfaceOutputMapPath: Qt.resolvedUrl("file:./output/map/surface.png")
    property string pressureOutputMapPath: Qt.resolvedUrl("file:./output/map/pressure.png")
    property string detailOutputMapPath: Qt.resolvedUrl("file:./output/map/detail.png")
    property string upperwind1OutputMapPath: Qt.resolvedUrl("file:./output/map/upperwind1.png")
    property string upperwind2OutputMapPath: Qt.resolvedUrl("file:./output/map/upperwind2.png")
    property string skewtOutputMapPath: Qt.resolvedUrl("file:./output/map/skewt.png")

    property bool isDataLoaded: false  // ✅ เริ่มต้นยังไม่ได้โหลด
    property bool plotSurfaceMap: false
    property bool plotPressureMap: false
    property bool plotDetailMap: false
    property bool plotUpperwind1Map: false
    property bool plotUpperwind2Map: false
    property bool plotSkewtMap: false

    property string progressText: "Loading Surface Map..."
    property bool isProgressVisible: false

    property string date: ""
    property string timeText: ""
    property int sliderValue: 0

    Connections {
        target: rootWindow
        function onFullscreenChanged(fullscreen) {
            root.isFullscreen = fullscreen;
            console.log("🖥 Fullscreen state updated:", fullscreen);
        }
    }

    Connections {
        target: rootWindow
        function onImagePathChanged(tabName, fileUrl) {
            console.log(tabName, fileUrl);
            if (tabName === "surface") {
                console.log("🖼️ Updated Map:", fileUrl);
                root.plotSurfaceMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ
                root.isProgressVisible = false;  // ✅ ซ่อน progress bar

                surfaceView.zoom = 0.98;
                surfaceView.offset = Qt.point(0, 0);
                surfaceView.zoomCenter = Qt.point(surfaceView.width / 2, surfaceView.height / 2);
            } else if (tabName === "pressure") {
                console.log("🖼️ Updated Map:", fileUrl);
                root.plotPressureMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ
                root.isProgressVisible = false;  // ✅ ซ่อน progress bar

                pressureView.zoom = 0.98;
                pressureView.offset = Qt.point(0, 0);
                pressureView.zoomCenter = Qt.point(pressureView.width / 2, pressureView.height / 2);
            } else if (tabName === "detail") {
                console.log("🖼️ Updated Map:", fileUrl);
                root.plotDetailMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ
                root.isProgressVisible = false;  // ✅ ซ่อน progress bar

                detailView.zoom = 0.98;
                detailView.offset = Qt.point(0, 0);
                detailView.zoomCenter = Qt.point(detailView.width / 2, detailView.height / 2);
            } else if (tabName === "wind_1") {
                console.log("🖼️ Updated Map:", fileUrl);
                root.plotUpperwind1Map = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ
                root.isProgressVisible = false;  // ✅ ซ่อน progress bar

                upperWind1View.zoom = 0.98;
                upperWind1View.offset = Qt.point(0, 0);
                upperWind1View.zoomCenter = Qt.point(upperWind1View.width / 2, upperWind1View.height / 2);
            } else if (tabName === "wind_2") {
                console.log("🖼️ Updated Map:", fileUrl);
                root.plotUpperwind2Map = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ
                root.isProgressVisible = false;  // ✅ ซ่อน progress bar

                upperWind2View.zoom = 0.98;
                upperWind2View.offset = Qt.point(0, 0);
                upperWind2View.zoomCenter = Qt.point(upperWind2View.width / 2, upperWind2View.height / 2);
            } else if (tabName === "skewt") {
                console.log("🖼️ Updated Map:", fileUrl);
                root.plotSkewtMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ
                root.isProgressVisible = false;  // ✅ ซ่อน progress bar

                SkewTView.zoom = 0.98;
                SkewTView.offset = Qt.point(0, 0);
                SkewTView.zoomCenter = Qt.point(SkewTView.width / 2, SkewTView.height / 2);
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#334a80"
        radius: root.isFullscreen ? 0 : 8
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
                color: minimizeArea.containsMouse ? "#e6a820" : "#ffbd2e"
                MouseArea {
                    id: minimizeArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: rootWindow.showMinimized()
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
                color: maximizeArea.containsMouse ? "#1fa734" : "#27c93f"
                MouseArea {
                    id: maximizeArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: rootWindow.toggleFullscreen()
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
                color: closeArea.containsMouse ? "#d43831" : "#ff5f56"
                MouseArea {
                    id: closeArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: rootWindow.closeApp()
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
                        onCurrentIndexChanged: {
                            root.currentIndex = currentIndex;   // เก็บ index ปัจจุบันไว้ใน property
                            root.isDataLoaded = false;          // สั่งให้โหลดข้อมูลใหม่ในแท็บนั้น
                        }

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

                        // 🖼️ SurfaceView
                        Rectangle {
                            id: surfaceView
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                            clip: true

                            property real zoom: 0.98
                            property point offset: Qt.point(0, 0)
                            property point zoomCenter: Qt.point(width / 2, height / 2)
                            property bool isDragging: false

                            // 🖼️ รูปแผนที่ Dynamic
                            DynamicImage {
                                id: surfaceViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: surfaceImageMapPath
                                dynamicSource: surfaceOutputMapPath
                                useDynamic: plotSurfaceMap

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

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: mouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(surfaceView.offset.x, surfaceView.offset.y);
                                        isDragging = true;
                                        cursorShape = Qt.ClosedHandCursor;
                                    }
                                }

                                onReleased: {
                                    isDragging = false;
                                    cursorShape = Qt.ArrowCursor;
                                }

                                onPositionChanged: mouse => {
                                    // อัพเดต zoomCenter เฉพาะเมื่อซูม (ใน onWheel)
                                    if (isDragging && (mouse.buttons & Qt.LeftButton)) {
                                        const dx = mouse.x - dragStartPos.x;
                                        const dy = mouse.y - dragStartPos.y;
                                        surfaceView.offset.x = imageStartOffset.x + dx;
                                        surfaceView.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = surfaceView.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        surfaceView.zoom = 0.98;
                                        surfaceView.offset = Qt.point(0, 0);
                                        surfaceView.zoomCenter = Qt.point(surfaceView.width / 2, surfaceView.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - surfaceView.offset.x) / oldZoom;
                                    const imageY = (mouseY - surfaceView.offset.y) / oldZoom;

                                    //surfaceView.offset.x = mouseX - imageX * newZoom;
                                    //surfaceView.offset.y = mouseY - imageY * newZoom;
                                    surfaceView.zoom = newZoom;
                                    surfaceView.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: resetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    surfaceView.zoom = 0.98;
                                    surfaceView.offset = Qt.point(0, 0);
                                    surfaceView.zoomCenter = Qt.point(surfaceView.width / 2, surfaceView.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${surfaceView.zoom.toFixed(2)} | Offset: (${surfaceView.offset.x.toFixed(0)}, ${surfaceView.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }

                        // 🖼️ PressureView
                        Rectangle {
                            id: pressureView
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                            clip: true

                            property real zoom: 0.98
                            property point offset: Qt.point(0, 0)
                            property point zoomCenter: Qt.point(width / 2, height / 2)
                            property bool isDragging: false

                            // 🖼️ รูปแผนที่ Dynamic
                            DynamicImage {
                                id: pressureViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: pressureImageMapPath
                                dynamicSource: pressureOutputMapPath
                                useDynamic: plotPressureMap

                                transform: [
                                    Translate {
                                        x: pressureView.offset.x
                                        y: pressureView.offset.y
                                    },
                                    Scale {
                                        origin.x: pressureView.zoomCenter.x
                                        origin.y: pressureView.zoomCenter.y
                                        xScale: pressureView.zoom
                                        yScale: pressureView.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: pressureViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(pressureView.offset.x, pressureView.offset.y);
                                        isDragging = true;
                                        cursorShape = Qt.ClosedHandCursor;
                                    }
                                }

                                onReleased: {
                                    isDragging = false;
                                    cursorShape = Qt.ArrowCursor;
                                }

                                onPositionChanged: mouse => {
                                    // อัพเดต zoomCenter เฉพาะเมื่อซูม (ใน onWheel)
                                    if (isDragging && (mouse.buttons & Qt.LeftButton)) {
                                        const dx = mouse.x - dragStartPos.x;
                                        const dy = mouse.y - dragStartPos.y;
                                        pressureView.offset.x = imageStartOffset.x + dx;
                                        pressureView.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = pressureView.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        pressureView.zoom = 0.98;
                                        pressureView.offset = Qt.point(0, 0);
                                        pressureView.zoomCenter = Qt.point(pressureView.width / 2, pressureView.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - pressureView.offset.x) / oldZoom;
                                    const imageY = (mouseY - pressureView.offset.y) / oldZoom;

                                    //pressureView.offset.x = mouseX - imageX * newZoom;
                                    //pressureView.offset.y = mouseY - imageY * newZoom;
                                    pressureView.zoom = newZoom;
                                    pressureView.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: pressureViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    pressureView.zoom = 0.98;
                                    pressureView.offset = Qt.point(0, 0);
                                    pressureView.zoomCenter = Qt.point(pressureView.width / 2, pressureView.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${pressureView.zoom.toFixed(2)} | Offset: (${pressureView.offset.x.toFixed(0)}, ${pressureView.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }

                        // 🖼️ DetailView
                        Rectangle {
                            id: detailView
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                            clip: true

                            property real zoom: 0.98
                            property point offset: Qt.point(0, 0)
                            property point zoomCenter: Qt.point(width / 2, height / 2)
                            property bool isDragging: false

                            // 🖼️ รูปแผนที่ Dynamic
                            DynamicImage {
                                id: detailViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: detailImageMapPath
                                dynamicSource: detailOutputMapPath
                                useDynamic: plotDetailMap

                                transform: [
                                    Translate {
                                        x: detailView.offset.x
                                        y: detailView.offset.y
                                    },
                                    Scale {
                                        origin.x: detailView.zoomCenter.x
                                        origin.y: detailView.zoomCenter.y
                                        xScale: detailView.zoom
                                        yScale: detailView.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: detailViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(detailView.offset.x, detailView.offset.y);
                                        isDragging = true;
                                        cursorShape = Qt.ClosedHandCursor;
                                    }
                                }

                                onReleased: {
                                    isDragging = false;
                                    cursorShape = Qt.ArrowCursor;
                                }

                                onPositionChanged: mouse => {
                                    // อัพเดต zoomCenter เฉพาะเมื่อซูม (ใน onWheel)
                                    if (isDragging && (mouse.buttons & Qt.LeftButton)) {
                                        const dx = mouse.x - dragStartPos.x;
                                        const dy = mouse.y - dragStartPos.y;
                                        detailView.offset.x = imageStartOffset.x + dx;
                                        detailView.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = detailView.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        detailView.zoom = 0.98;
                                        detailView.offset = Qt.point(0, 0);
                                        detailView.zoomCenter = Qt.point(detailView.width / 2, detailView.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - detailView.offset.x) / oldZoom;
                                    const imageY = (mouseY - detailView.offset.y) / oldZoom;

                                    //detailView.offset.x = mouseX - imageX * newZoom;
                                    //detailView.offset.y = mouseY - imageY * newZoom;
                                    detailView.zoom = newZoom;
                                    detailView.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: detailViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    detailView.zoom = 0.98;
                                    detailView.offset = Qt.point(0, 0);
                                    detailView.zoomCenter = Qt.point(detailView.width / 2, detailView.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${detailView.zoom.toFixed(2)} | Offset: (${detailView.offset.x.toFixed(0)}, ${detailView.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }

                        // 🖼️ UpperWind1View
                        Rectangle {
                            id: upperWind1View
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                            clip: true

                            property real zoom: 0.98
                            property point offset: Qt.point(0, 0)
                            property point zoomCenter: Qt.point(width / 2, height / 2)
                            property bool isDragging: false

                            // 🖼️ รูปแผนที่ Dynamic
                            DynamicImage {
                                id: upperWind1ViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: upperwind1ImageMapPath
                                dynamicSource: upperwind1OutputMapPath
                                useDynamic: plotUpperwind1Map

                                transform: [
                                    Translate {
                                        x: upperWind1View.offset.x
                                        y: upperWind1View.offset.y
                                    },
                                    Scale {
                                        origin.x: upperWind1View.zoomCenter.x
                                        origin.y: upperWind1View.zoomCenter.y
                                        xScale: upperWind1View.zoom
                                        yScale: upperWind1View.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: upperWind1ViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(upperWind1View.offset.x, upperWind1View.offset.y);
                                        isDragging = true;
                                        cursorShape = Qt.ClosedHandCursor;
                                    }
                                }

                                onReleased: {
                                    isDragging = false;
                                    cursorShape = Qt.ArrowCursor;
                                }

                                onPositionChanged: mouse => {
                                    // อัพเดต zoomCenter เฉพาะเมื่อซูม (ใน onWheel)
                                    if (isDragging && (mouse.buttons & Qt.LeftButton)) {
                                        const dx = mouse.x - dragStartPos.x;
                                        const dy = mouse.y - dragStartPos.y;
                                        upperWind1View.offset.x = imageStartOffset.x + dx;
                                        upperWind1View.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = upperWind1View.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        upperWind1View.zoom = 0.98;
                                        upperWind1View.offset = Qt.point(0, 0);
                                        upperWind1View.zoomCenter = Qt.point(upperWind1View.width / 2, upperWind1View.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - upperWind1View.offset.x) / oldZoom;
                                    const imageY = (mouseY - upperWind1View.offset.y) / oldZoom;

                                    //upperWind1View.offset.x = mouseX - imageX * newZoom;
                                    //upperWind1View.offset.y = mouseY - imageY * newZoom;
                                    upperWind1View.zoom = newZoom;
                                    upperWind1View.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: upperWind1ViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    upperWind1View.zoom = 0.98;
                                    upperWind1View.offset = Qt.point(0, 0);
                                    upperWind1View.zoomCenter = Qt.point(upperWind1View.width / 2, upperWind1View.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${upperWind1View.zoom.toFixed(2)} | Offset: (${upperWind1View.offset.x.toFixed(0)}, ${upperWind1View.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }

                        // 🖼️ UpperWind2View
                        Rectangle {
                            id: upperWind2View
                            color: "#e3f2fd"
                            anchors.fill: parent
                            bottomLeftRadius: 8
                            bottomRightRadius: 8
                            clip: true

                            property real zoom: 0.98
                            property point offset: Qt.point(0, 0)
                            property point zoomCenter: Qt.point(width / 2, height / 2)
                            property bool isDragging: false

                            // 🖼️ รูปแผนที่ Dynamic
                            DynamicImage {
                                id: upperWind2ViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: upperwind2ImageMapPath
                                dynamicSource: upperwind2OutputMapPath
                                useDynamic: plotUpperwind2Map

                                transform: [
                                    Translate {
                                        x: upperWind2View.offset.x
                                        y: upperWind2View.offset.y
                                    },
                                    Scale {
                                        origin.x: upperWind2View.zoomCenter.x
                                        origin.y: upperWind2View.zoomCenter.y
                                        xScale: upperWind2View.zoom
                                        yScale: upperWind2View.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: upperWind2ViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(upperWind2View.offset.x, upperWind2View.offset.y);
                                        isDragging = true;
                                        cursorShape = Qt.ClosedHandCursor;
                                    }
                                }

                                onReleased: {
                                    isDragging = false;
                                    cursorShape = Qt.ArrowCursor;
                                }

                                onPositionChanged: mouse => {
                                    // อัพเดต zoomCenter เฉพาะเมื่อซูม (ใน onWheel)
                                    if (isDragging && (mouse.buttons & Qt.LeftButton)) {
                                        const dx = mouse.x - dragStartPos.x;
                                        const dy = mouse.y - dragStartPos.y;
                                        upperWind2View.offset.x = imageStartOffset.x + dx;
                                        upperWind2View.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = upperWind2View.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        upperWind2View.zoom = 0.98;
                                        upperWind2View.offset = Qt.point(0, 0);
                                        upperWind2View.zoomCenter = Qt.point(upperWind2View.width / 2, upperWind2View.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - upperWind2View.offset.x) / oldZoom;
                                    const imageY = (mouseY - upperWind2View.offset.y) / oldZoom;

                                    //upperWind2View.offset.x = mouseX - imageX * newZoom;
                                    //upperWind2View.offset.y = mouseY - imageY * newZoom;
                                    upperWind2View.zoom = newZoom;
                                    upperWind2View.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: upperWind2ViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    upperWind2View.zoom = 0.98;
                                    upperWind2View.offset = Qt.point(0, 0);
                                    upperWind2View.zoomCenter = Qt.point(upperWind2View.width / 2, upperWind2View.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${upperWind2View.zoom.toFixed(2)} | Offset: (${upperWind2View.offset.x.toFixed(0)}, ${upperWind2View.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }
                        // 📈 SkewTView
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
                        visible: root.currentIndex != 5  // ✅ ไม่แสดงเฉพาะ tab Skew-T
                    }

                    Slider {
                        id: dataSlider
                        from: 50
                        to: 100
                        value: 70
                        Layout.fillWidth: true
                        stepSize: 1
                        visible: root.currentIndex != 5  // ✅ ไม่แสดงเฉพาะ tab Skew-T

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
                        visible: root.currentIndex === 5  // ✅ แสดงเฉพาะ tab Skew-T
                    }

                    RowLayout {
                        spacing: 16
                        visible: root.currentIndex === 5  // ✅ แสดงเฉพาะ tab Skew-T
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
                                onClicked: {
                                    let selectedDate = datePicker.date.toLocaleDateString(Qt.locale("en_US"), "yyyy-MM-dd");
                                    let selectedTime = timeSelector.currentText;
                                    let dataSliderValue = Math.round(dataSlider.value);

                                    rootWindow.load_data(selectedDate, selectedTime, dataSliderValue, tabBar.currentIndex);
                                    //root.isDataLoaded = true;  // ✅ หลังโหลดสำเร็จแล้ว
                                }
                            }
                        }

                        // 📊 Table Viewer
                        Control {
                            id: tableButton
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            implicitHeight: 30
                            enabled: root.isDataLoaded  // ✅ ใช้ property นี้

                            background: Rectangle {
                                color: tableButton.hovered ? "#d1d1d1" : "#fff"  // สี hover
                                radius: 6
                                opacity: tableButton.enabled ? 1.0 : 0.5  // ✅ ทำให้จางลงถ้ากดไม่ได้
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
                                enabled: tableButton.enabled  // ✅ ตรงนี้สำคัญมาก
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
                        enabled: root.isDataLoaded  // ✅ ใช้ property นี้

                        background: Rectangle {
                            color: plotButton.hovered ? "#d1d1d1" : "#fff"
                            radius: 6
                            opacity: plotButton.enabled ? 1.0 : 0.5  // ✅ ทำให้จางลงถ้ากดไม่ได้
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
                            enabled: plotButton.enabled  // ✅ ตรงนี้สำคัญมาก
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onEntered: plotButton.hovered = true
                            onExited: plotButton.hovered = false
                            onClicked: {
                                // ✅ 1. แสดง Progress Overlay ก่อนทันที
                                root.isProgressVisible = true;

                                // ✅ 2. Reset Flag (ถ้ามี)
                                root.isDataLoaded = false;

                                // ✅ 3. เรียกไปสั่ง Python plot
                                Qt.callLater(function () {
                                    rootWindow.buttonClicked("plot:" + tabBar.currentItem.text);
                                });
                            }
                        }
                    }

                    // 📄 Save PDF + 📸 Save PNG + 📂 Open File
                    RowLayout {
                        Layout.columnSpan: 2
                        spacing: 10

                        // 📄 Save PDF
                        Control {
                            id: pdfButton
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            implicitHeight: 30
                            visible: root.currentIndex === 5  // ✅ แสดงเฉพาะ tab Skew-T

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
                            visible: root.currentIndex != 5  // ✅ แสดงเฉพาะ tab Skew-T

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
            }

            GroupBox {
                id: checkCodeDebugger
                title: "CheckCode Debugger"
                Layout.column: 1
                Layout.row: 1
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 100  // ควรกำหนดค่าต่ำสุดเป็นค่าคงที่
                Layout.preferredWidth: parent.width * 0.15
                Layout.maximumWidth: parent.width * 0.2

                label: Item {
                    width: parent.width * 0.6
                    height: 20
                    anchors.left: parent.left
                    anchors.leftMargin: 10

                    Rectangle {
                        anchors.fill: parent
                        color: "#e3f2fd"
                        radius: 6
                        antialiasing: true
                        Text {
                            anchors.centerIn: parent
                            text: checkCodeDebugger.title
                            font.pixelSize: 14
                            font.bold: true
                            color: "#1b2a4b"
                        }
                    }
                }

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        TextArea {
                            id: debugTextArea
                            objectName: "debugTextArea"
                            text: root.debugText
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            font.pixelSize: 10
                            color: "white"
                            padding: 2
                            selectByMouse: true

                            background: Rectangle {
                                color: "#1b2a4b"
                                radius: 6
                                border.color: "#90caf9"
                                border.width: 1
                            }

                            onTextChanged: {
                                cursorPosition = length;
                                if (ScrollBar.vertical) {
                                    ScrollBar.vertical.position = 1.0 - ScrollBar.vertical.size;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

//MessageDialog {
//    id: dateDialog
//    title: "📅 Selected Date"
//    text: ""
//    visible: false
//    onAccepted: console.log("✅ Dialog closed")
//}
//
//dateDialog.text = "คุณเลือกวันที่: " + selectedDate + " | " + selectedTime + " | " + dataSliderValue + "%";
//dateDialog.visible = true;
// ✅ MainWindow.qml
