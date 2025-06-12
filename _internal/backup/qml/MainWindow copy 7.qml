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

    property int currentIndex: 0 // ✅ เก็บ index ของแท็บปัจจุบัน
    property string currentTab: tabBar.currentItem.text // ✅ เก็บชื่อแท็บปัจจุบัน
    property bool isFullscreen: false // ✅ สถานะ fullscreen
    property string debugText: "" // ✅ ข้อความสำหรับ debug
    property string surfaceImageMapPath: Qt.resolvedUrl("../../images/map/surface.png") // ✅ เริ่มต้นยังไม่มีเส้นทางไฟล์แผนที่
    property string pressureImageMapPath: Qt.resolvedUrl("../../images/map/pressure.png") // ✅ เริ่มต้นยังไม่มีเส้นทางไฟล์แผนที่
    property string detailImageMapPath: Qt.resolvedUrl("../../images/map/detail.png") // ✅ เริ่มต้นยังไม่มีเส้นทางไฟล์แผนที่
    property string upperwind1ImageMapPath: Qt.resolvedUrl("../../images/map/upperwind1.png") // ✅ เริ่มต้นยังไม่มีเส้นทางไฟล์แผนที่
    property string upperwind2ImageMapPath: Qt.resolvedUrl("../../images/map/upperwind2.png") // ✅ เริ่มต้นยังไม่มีเส้นทางไฟล์แผนที่
    property string skewtImageMapPath: Qt.resolvedUrl("../../images/map/skewt.png") // ✅ เริ่มต้นยังไม่มีเส้นทางไฟล์แผนที่

    property string surfaceOutputMapPath: Qt.resolvedUrl("../../output/map/surface.png") // ✅ เริ่มต้นยังไม่มี output map
    property string pressureOutputMapPath: Qt.resolvedUrl("../../output/map/pressure.png") // ✅ เริ่มต้นยังไม่มี output map
    property string detailOutputMapPath: Qt.resolvedUrl("../../output/map/detail.png") // ✅ เริ่มต้นยังไม่มี output map
    property string upperwind1OutputMapPath: Qt.resolvedUrl("../../output/map/upperwind1.png") // ✅ เริ่มต้นยังไม่มี output map
    property string upperwind2OutputMapPath: Qt.resolvedUrl("../../output/map/upperwind2.png")  // ✅ เริ่มต้นยังไม่มี output map
    property string skewtOutputMapPath: Qt.resolvedUrl("../../output/map/skewt.png") // ✅ เริ่มต้นยังไม่มี output map

    property bool isDataCheckURL: false  // ✅ เริ่มต้นยังไม่ได้ตรวจสอบ URL
    property bool isDataLoaded: false  // ✅ เริ่มต้นยังไม่ได้โหลด
    property bool plotSurfaceMap: false // ✅ สถานะการแสดงผลแผนที่
    property bool plotPressureMap: false // ✅ สถานะการแสดงผลแผนที่
    property bool plotDetailMap: false // ✅ สถานะการแสดงผลแผนที่
    property bool plotUpperwind1Map: false // ✅ สถานะการแสดงผลแผนที่
    property bool plotUpperwind2Map: false  // ✅ สถานะการแสดงผลแผนที่
    property bool plotSkewtMap: false

    // ✅ เชื่อมต่อกับ rootWindow เพื่อรับการแจ้งเตือนเมื่อมีการเปลี่ยนแปลงสถานะ fullscreen
    Connections {
        target: rootWindow
        function onFullscreenChanged(fullscreen) {
            root.isFullscreen = fullscreen;
            console.log("🖥 Fullscreen state updated:", fullscreen);
        }
    }

    // ✅ เชื่อมต่อกับ rootWindow เพื่อรับการแจ้งเตือนเมื่อมีการอัพเดตแผนที่
    Connections {
        target: rootWindow
        function onImagePathChanged(tabName, fileUrl) {
            let current = debugTextArea.text;
            debugTextArea.text = "";         // ล้างชั่วคราว
            debugTextArea.text = current;    // ใส่คืน

            if (tabName === "surface") {
                root.plotSurfaceMap = false;  // ✅ รีเซ็ตสถานะการแสดงผลแผนที่
                //surfaceImageMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                root.surfaceOutputMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ output
                root.surfaceOutputMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ output
                root.plotSurfaceMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ

                surfaceView.zoom = 0.98;
                surfaceView.offset = Qt.point(0, 0);
                surfaceView.zoomCenter = Qt.point(surfaceView.width / 2, surfaceView.height / 2);

                msgDialog.message = "🗺️ Plot Surface อต.ทอ. 1001\nComplete";
                msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
            } else if (tabName === "pressure") {
                root.plotPressureMap = false;  // ✅ รีเซ็ตสถานะการแสดงผลแผนที่
                //pressureImageMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                root.pressureOutputMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ output
                root.pressureOutputMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ output
                root.plotPressureMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ

                pressureView.zoom = 0.98;
                pressureView.offset = Qt.point(0, 0);
                pressureView.zoomCenter = Qt.point(pressureView.width / 2, pressureView.height / 2);

                msgDialog.message = "🗺️ Plot Pressure Map อต.ทอ. 1010\nComplete";
                msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
            } else if (tabName === "detail") {
                root.plotDetailMap = false;  // ✅ รีเซ็ตสถานะการแสดงผลแผนที่
                //detailImageMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                root.detailOutputMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ output
                root.detailOutputMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ output
                root.plotDetailMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ

                detailView.zoom = 0.98;
                detailView.offset = Qt.point(0, 0);
                detailView.zoomCenter = Qt.point(detailView.width / 2, detailView.height / 2);

                msgDialog.message = "🗺️ Plot Detail Map อต.ทอ. 1003\nComplete";
                msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
            } else if (tabName === "wind_1") {
                root.plotUpperwind1Map = false;  // ✅ รีเซ็ตสถานะการแสดงผลแผนที่
                //upperWind1ImageMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                //upperWind1ImageMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                //root.upperWind1OutputMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ output
                //root.upperWind1OutputMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ output
                root.plotUpperwind1Map = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ

                upperwind1View.zoom = 0.98;
                upperwind1View.offset = Qt.point(0, 0);
                upperwind1View.zoomCenter = Qt.point(upperwind1View.width / 2, upperwind1View.height / 2);

                msgDialog.message = "🗺️ Plot Wind 1 Map อต.ทอ. 1002\nComplete";
                msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
            } else if (tabName === "wind_2") {
                root.plotUpperwind2Map = false;  // ✅ รีเซ็ตสถานะการแสดงผลแผนที่
                //upperWind2ImageMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                //upperWind2ImageMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                //root.upperWind2OutputMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ output
                //root.upperWind2OutputMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ output
                root.plotUpperwind2Map = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ

                upperwind2View.zoom = 0.98;
                upperwind2View.offset = Qt.point(0, 0);
                upperwind2View.zoomCenter = Qt.point(upperwind2View.width / 2, upperwind2View.height / 2);

                msgDialog.message = "🗺️ Plot Wind 2 Map อต.ทอ. 1013\nComplete";
                msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
            } else if (tabName === "skewt") {
                root.plotSkewtMap = false;  // ✅ รีเซ็ตสถานะการแสดงผลแผนที่
                root.skewtImageMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                root.skewtImageMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ต้นฉบับ
                //root.skewtOutputMapPath = "";  // ✅ อัพเดตเส้นทางไฟล์ output
                //root.skewtOutputMapPath = fileUrl;  // ✅ อัพเดตเส้นทางไฟล์ output
                root.plotSkewtMap = true;  // ✅ ใช้ภาพ output แทนภาพต้นฉบับ

                skewtView.zoom = 0.98;
                skewtView.offset = Qt.point(0, 0);
                skewtView.zoomCenter = Qt.point(skewtView.width / 2, skewtView.height / 2);

                msgDialog.message = "🗺️ Plot Wind 2 Map อต.ทอ. 1011\nComplete";
                msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
            }
        }
    }

    // ✅ เชื่อมต่อกับ rootWindow เพื่อรับการแจ้งเตือนตรวจสอบอินเทอร์เน็ตเสร็จสิ้น
    Connections {
        target: rootWindow
        function onDataCheckURL(loaded) {
            root.isDataCheckURL = loaded;

            msgDialog.message = loaded ? "🌏 Connection successfully!" : "❌ Connection failed!";
            msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
        }
    }

    // ✅ เชื่อมต่อกับ rootWindow เพื่อรับการแจ้งเตือนเมื่อโหลดข้อมูลเสร็จสิ้น
    Connections {
        target: rootWindow
        function onDataLoadedChanged(loaded) {
            let current = debugTextArea.text;
            debugTextArea.text = "";         // ล้างชั่วคราว
            debugTextArea.text = current;    // ใส่คืน

            root.isDataLoaded = loaded;
            msgDialog.message = loaded ? "🌏 Data loaded successfully!" : "❌ Failed to load data.";
            msgDialog.open();  // ✅ เปิด Dialog อย่างถูกต้อง
        }
    }

    // ✅ Dialog สำหรับแสดงข้อความ
    Dialog {
        id: msgDialog
        title: ""
        modal: true
        x: (parent.width - width) / 2  // ✅ จัดให้อยู่กลางแนวนอน
        y: (parent.height - height) / 2  // ✅ จัดให้อยู่กลางแนวตั้ง
        width: 340
        height: 120
        property string message: ""

        background: Rectangle {
            color: "#d8334a80"
            radius: 16
        }

        contentItem: Column {
            spacing: 10
            anchors.fill: parent
            anchors.margins: 24
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            Text {
                text: msgDialog.message
                font.pixelSize: 16
                font.bold: true
                color: "#fff"
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }

            //
            Control {
                id: msgButton
                anchors.horizontalCenter: parent.horizontalCenter
                Layout.columnSpan: 2
                implicitHeight: 30
                implicitWidth: 100

                background: Rectangle {
                    color: msgButton.hovered ? "#d39b00" : "#f5bd24"  // สี hover
                    radius: 6
                }

                contentItem: Label {
                    text: "ปิดหน้าต่าง"
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
                    onEntered: msgButton.hovered = true
                    onExited: msgButton.hovered = false
                    onClicked: msgDialog.close()
                }
            }
        }
    }

    Connections {
        target: rootWindow
        function onVersionLoader(vName) {
            titleLabel.text = "Meteorological Plotting System - v." + vName;
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
                text: ""
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
                            id: upperwind1View
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
                                id: upperwind1ViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: upperwind1ImageMapPath
                                dynamicSource: upperwind1OutputMapPath
                                useDynamic: plotUpperwind1Map

                                transform: [
                                    Translate {
                                        x: upperwind1View.offset.x
                                        y: upperwind1View.offset.y
                                    },
                                    Scale {
                                        origin.x: upperwind1View.zoomCenter.x
                                        origin.y: upperwind1View.zoomCenter.y
                                        xScale: upperwind1View.zoom
                                        yScale: upperwind1View.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: upperwind1ViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(upperwind1View.offset.x, upperwind1View.offset.y);
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
                                        upperwind1View.offset.x = imageStartOffset.x + dx;
                                        upperwind1View.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = upperwind1View.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        upperwind1View.zoom = 0.98;
                                        upperwind1View.offset = Qt.point(0, 0);
                                        upperwind1View.zoomCenter = Qt.point(upperwind1View.width / 2, upperwind1View.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - upperwind1View.offset.x) / oldZoom;
                                    const imageY = (mouseY - upperwind1View.offset.y) / oldZoom;

                                    //upperwind1View.offset.x = mouseX - imageX * newZoom;
                                    //upperwind1View.offset.y = mouseY - imageY * newZoom;
                                    upperwind1View.zoom = newZoom;
                                    upperwind1View.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: upperwind1ViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    upperwind1View.zoom = 0.98;
                                    upperwind1View.offset = Qt.point(0, 0);
                                    upperwind1View.zoomCenter = Qt.point(upperwind1View.width / 2, upperwind1View.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${upperwind1View.zoom.toFixed(2)} | Offset: (${upperwind1View.offset.x.toFixed(0)}, ${upperwind1View.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }

                        // 🖼️ UpperWind2View
                        Rectangle {
                            id: upperwind2View
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
                                id: upperwind2ViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: upperwind2ImageMapPath
                                dynamicSource: upperwind2OutputMapPath
                                useDynamic: plotUpperwind2Map

                                transform: [
                                    Translate {
                                        x: upperwind2View.offset.x
                                        y: upperwind2View.offset.y
                                    },
                                    Scale {
                                        origin.x: upperwind2View.zoomCenter.x
                                        origin.y: upperwind2View.zoomCenter.y
                                        xScale: upperwind2View.zoom
                                        yScale: upperwind2View.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: upperwind2ViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(upperwind2View.offset.x, upperwind2View.offset.y);
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
                                        upperwind2View.offset.x = imageStartOffset.x + dx;
                                        upperwind2View.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = upperwind2View.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        upperwind2View.zoom = 0.98;
                                        upperwind2View.offset = Qt.point(0, 0);
                                        upperwind2View.zoomCenter = Qt.point(upperwind2View.width / 2, upperwind2View.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - upperwind2View.offset.x) / oldZoom;
                                    const imageY = (mouseY - upperwind2View.offset.y) / oldZoom;

                                    //upperwind2View.offset.x = mouseX - imageX * newZoom;
                                    //upperwind2View.offset.y = mouseY - imageY * newZoom;
                                    upperwind2View.zoom = newZoom;
                                    upperwind2View.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: upperwind2ViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    upperwind2View.zoom = 0.98;
                                    upperwind2View.offset = Qt.point(0, 0);
                                    upperwind2View.zoomCenter = Qt.point(upperwind2View.width / 2, upperwind2View.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${upperwind2View.zoom.toFixed(2)} | Offset: (${upperwind2View.offset.x.toFixed(0)}, ${upperwind2View.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
                        }

                        // 📈 SkewTView
                        Rectangle {
                            id: skewtView
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
                                id: skewtViewZoomableImage
                                anchors.fill: parent
                                fallbackSource: skewtImageMapPath
                                dynamicSource: skewtOutputMapPath
                                useDynamic: plotskewtMap

                                transform: [
                                    Translate {
                                        x: skewtView.offset.x
                                        y: skewtView.offset.y
                                    },
                                    Scale {
                                        origin.x: skewtView.zoomCenter.x
                                        origin.y: skewtView.zoomCenter.y
                                        xScale: skewtView.zoom
                                        yScale: skewtView.zoom
                                    }
                                ]
                            }

                            // ✅ MouseArea สำหรับการซูมและเลื่อนภาพ
                            MouseArea {
                                id: skewtViewMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.ArrowCursor

                                property point dragStartPos
                                property point imageStartOffset
                                property bool isDragging: false

                                onPressed: mouse => {
                                    if (mouse.button === Qt.LeftButton) {
                                        dragStartPos = Qt.point(mouse.x, mouse.y);
                                        imageStartOffset = Qt.point(skewtView.offset.x, skewtView.offset.y);
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
                                        skewtView.offset.x = imageStartOffset.x + dx;
                                        skewtView.offset.y = imageStartOffset.y + dy;
                                    }
                                }

                                onWheel: wheel => {
                                    const oldZoom = skewtView.zoom;
                                    const zoomFactor = wheel.angleDelta.y > 0 ? 1.1 : 0.98;
                                    const newZoom = Math.max(0.98, Math.min(oldZoom * zoomFactor, 50.0));

                                    // รีเซ็ตเฉพาะตอนซูมออกกลับมา 0.98
                                    if (wheel.angleDelta.y < 0 && Math.abs(newZoom - 0.98) < 0.001) {
                                        skewtView.zoom = 0.98;
                                        skewtView.offset = Qt.point(0, 0);
                                        skewtView.zoomCenter = Qt.point(skewtView.width / 2, skewtView.height / 2);
                                        return;
                                    }

                                    const mouseX = wheel.x;
                                    const mouseY = wheel.y;
                                    const imageX = (mouseX - skewtView.offset.x) / oldZoom;
                                    const imageY = (mouseY - skewtView.offset.y) / oldZoom;

                                    //skewtView.offset.x = mouseX - imageX * newZoom;
                                    //skewtView.offset.y = mouseY - imageY * newZoom;
                                    skewtView.zoom = newZoom;
                                    skewtView.zoomCenter = Qt.point(mouseX, mouseY);
                                }
                            }

                            Button {
                                id: skewtViewResetZoomButton
                                text: "Reset Zoom"
                                anchors.left: parent.left
                                anchors.bottom: parent.bottom
                                anchors.leftMargin: 5 // ห่างจากด้านซ้าย 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                font.pixelSize: 12
                                onClicked: {
                                    skewtView.zoom = 0.98;
                                    skewtView.offset = Qt.point(0, 0);
                                    skewtView.zoomCenter = Qt.point(skewtView.width / 2, skewtView.height / 2);
                                }
                            }

                            Text {
                                anchors.bottom: parent.bottom
                                anchors.right: parent.right
                                anchors.rightMargin: 5  // ห่างจากด้านขวา 5 หน่วย
                                anchors.bottomMargin: 5 // ห่างจากด้านล่าง 5 หน่วย
                                text: `Zoom: ${skewtView.zoom.toFixed(2)} | Offset: (${skewtView.offset.x.toFixed(0)}, ${skewtView.offset.y.toFixed(0)})`
                                color: "black"
                                font.pixelSize: 12
                                visible: true
                            }
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
                        onClicked: date => {
                            //console.log("📅 Date selected:", date.toDateString());
                            root.isDataLoaded = false;  // ✅ รีเซตสถานะโหลดข้อมูล
                        }
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

                    // 🆔 Station
                    Label {
                        text: "🆔 Station:"
                        color: "#fff"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignLeft
                        visible: root.currentIndex === 5  // ✅ แสดงเฉพาะ tab Skew-T
                    }

                    ComboBox {
                        id: stationSelector
                        Layout.fillWidth: true
                        font.pixelSize: 10
                        model: ["48327| VTCC| Chiang Mai", "48378| VTPS| Phitsanulok", "48381| VTUK| Khon Kaen", "48407| VTUU| Ubon Ratchathani", "48431| VTUN| Nakhon Ratchasima", "48453| VTBB| Bangna", "48477| VTxx| Sattahip", "48480| VTBC| Chanthaburi", "48500| VTBP| Prachuap Khirikhan", "48551| VTSB| Surat Thani", "48565| VTSP| Phuket", "48568| VTSH| Songkhla",]
                        currentIndex: 0
                        visible: root.currentIndex === 5  // ✅ แสดงเฉพาะ tab Skew-T

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

                            highlighted: stationSelector.highlightedIndex === index
                        }

                        contentItem: Text {
                            leftPadding: 5
                            text: stationSelector.displayText
                            font.pixelSize: 10
                            color: "#1b2a4b"
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }

                        indicator: Canvas {
                            id: stationIndicator
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
                            enabled: root.isDataCheckURL  // ✅ ปิดการใช้งานถ้าไม่สามารถโหลดข้อมูลได้

                            background: Rectangle {
                                color: loadButton.hovered ? "#d1d1d1" : "#fff"  // สี hover
                                radius: 6
                                opacity: loadButton.enabled ? 1.0 : 0.5  // ✅ จางลงถ้า disabled
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
                                enabled: loadButton.enabled  // ✅ ปิดการใช้งาน MouseArea ถ้าไม่สามารถโหลดข้อมูลได้
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onEntered: loadButton.hovered = true
                                onExited: loadButton.hovered = false
                                onClicked: {
                                    msgDialog.message = "⏳ Waiting load data...!";
                                    msgDialog.open();  // ✅ เปิด Dialog ก่อน

                                    // ✅ รอให้ msgDialog แสดงก่อน แล้วค่อยโหลดข้อมูล
                                    loadDelayTimer.start();
                                }
                            }

                            // วางไว้ใน scope เดียวกับ MouseArea (เช่นใน Item เดียวกัน)
                            Timer {
                                id: loadDelayTimer
                                interval: 100  // หน่วง 100 มิลลิวินาที
                                repeat: false
                                running: false
                                onTriggered: {
                                    let selectedDate = datePicker.date.toLocaleDateString(Qt.locale("en_US"), "yyyy-MM-dd");
                                    let selectedTime = timeSelector.currentText;
                                    let station = stationSelector.currentText;
                                    let tabIndex = tabBar.currentIndex;

                                    if (tabIndex === 5) {
                                        rootWindow.load_data(selectedDate, selectedTime, station, tabIndex);
                                    } else {
                                        rootWindow.load_data(selectedDate, selectedTime, "", tabIndex);
                                    }
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
                                //onClicked: rootWindow.buttonClicked("table")
                                onClicked: rootWindow.table_view(tabBar.currentIndex)
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
                                msgDialog.message = "⏳ Waiting Plot...!\n" + tabBar.currentItem.text;
                                msgDialog.open();  // ✅ เปิด Dialog ก่อน

                                // ✅ รอให้ msgDialog แสดงก่อน แล้วค่อยโหลดข้อมูล
                                plotDelayTimer.start();
                            }
                        }

                        // วางไว้ใน scope เดียวกับ MouseArea (เช่นใน Item เดียวกัน)
                        Timer {
                            id: plotDelayTimer
                            interval: 100  // หน่วง 100 มิลลิวินาที
                            repeat: false
                            running: false
                            onTriggered: {
                                let selectedDate = datePicker.date.toLocaleDateString(Qt.locale("en_US"), "yyyy-MM-dd");
                                let selectedTime = timeSelector.currentText;
                                let dataSliderValue = Math.round(dataSlider.value);
                                let station = stationSelector.currentText;
                                let tabName = tabBar.currentItem.text;
                                let tabIndex = tabBar.currentIndex;
                                let radioButtonChecked = sfcRadio.checked ? "SFC" : "925mb";

                                if (tabIndex === 5) {
                                    rootWindow.plot_map_by_tab(selectedDate, selectedTime, "", station, radioButtonChecked, tabName);
                                } else {
                                    rootWindow.plot_map_by_tab(selectedDate, selectedTime, dataSliderValue, "", "", tabName);
                                }
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
                                //onClicked: rootWindow.buttonClicked("pdf")
                                onClicked: {
                                    let selectedDate = datePicker.date.toLocaleDateString(Qt.locale("en_US"), "yyyy-MM-dd");
                                    let selectedTime = timeSelector.currentText;
                                    let station = stationSelector.currentText;

                                    rootWindow.save_pdf(selectedDate, selectedTime, station, tabBar.currentIndex);
                                }
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
                                //onClicked: rootWindow.buttonClicked("png:" + tabBar.currentIndex)
                                onClicked: {
                                    let selectedDate = datePicker.date.toLocaleDateString(Qt.locale("en_US"), "yyyy-MM-dd");
                                    let selectedTime = timeSelector.currentText;

                                    rootWindow.save_png(selectedDate, selectedTime, tabBar.currentIndex);
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
                                //onClicked: rootWindow.buttonClicked("open")
                                onClicked: {
                                    rootWindow.open_text_file(tabBar.currentIndex);
                                }
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

                        property bool scrollbarVisible: vScroll.size < 1.0

                        ScrollBar.vertical: ScrollBar {
                            id: vScroll
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: 6
                            policy: ScrollBar.AsNeeded
                            active: true
                            interactive: true

                            contentItem: Rectangle {
                                implicitWidth: 6
                                radius: 6
                                color: "#1b2a4a"
                                opacity: 1
                            }

                            background: Rectangle {
                                radius: 0
                                color: "#fff"
                                opacity: 1
                            }
                        }

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
                                border.color: "#90caf9"
                                border.width: 1

                                // ✅ ปรับ radius ตามสถานะ scrollbar
                                topLeftRadius: 6
                                bottomLeftRadius: 6
                                topRightRadius: scrollbarVisible ? 0 : 6
                                bottomRightRadius: scrollbarVisible ? 0 : 6

                                // ✅ เพิ่มความลื่นไหลเวลาเปลี่ยน (ไม่จำเป็นแต่ดูดี)
                                Behavior on topRightRadius {
                                    NumberAnimation {
                                        duration: 150
                                    }
                                }
                                Behavior on bottomRightRadius {
                                    NumberAnimation {
                                        duration: 150
                                    }
                                }
                            }

                            onTextChanged: cursorPosition = length
                        }
                    }
                }
            }
        }
    }
}
