// File: ui/qml/splash_orbit.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Shapes 1.15  // สำหรับ PathArc

Rectangle {
    id: splash
    width: 380
    height: 420
    color: "#1b2a4b"
    radius: 16

    property bool setUpdateAvailable: false

    Connections {
        target: splashWindow
        function onVersionLoader(vName) {
            versionLabel.text = "MPS-Version: " + vName;
        }
    }

    Connections {
        target: splashWindow
        function onVersionUpdate(updateAvailable) {
            setUpdateAvailable = updateAvailable;
        }
    }

    // 🪐 Canvas สำหรับเส้นวงโคจร (อยู่หลัง)
    Canvas {
        id: orbitCanvas
        anchors.fill: parent
        z: 0

        onPaint: {
            let ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);

            ctx.save(); // 🔒 เก็บค่าปัจจุบันไว้ก่อน
            ctx.globalAlpha = 0.7; // 👈 ความโปร่งใส 0.0 - 1.0

            ctx.strokeStyle = "#334a80";
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);

            let cx = width / 2;
            let cy = height / 2;

            [60, 90, 120, 150, 190, 230, 270, 310].forEach(radius => {
                ctx.beginPath();
                ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
                ctx.stroke();
            });

            ctx.restore(); // 🔓 คืนค่าที่ save ไว้
        }

        Component.onCompleted: requestPaint()
    }

    // 🌞 โลโก้กลาง
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20
        z: 2

        Image {
            id: logo
            source: "../../images/icons/logowxao-6.png"
            width: 120
            height: 120
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
        }

        // Username
        TextField {
            id: usernameField
            implicitHeight: 30  // ✅ ปรับตรงนี้เลย
            placeholderText: "Username"
            Layout.fillWidth: true
            font.pixelSize: 14
            background: Rectangle {
                color: "white"
                radius: 8
                border.color: "#F4B400"
                border.width: 1
            }
        }

        // Password
        TextField {
            id: passwordField
            implicitHeight: 30  // ✅ ปรับตรงนี้เลย
            placeholderText: "Password"
            echoMode: TextInput.Password
            Layout.fillWidth: true
            font.pixelSize: 14
            background: Rectangle {
                color: "white"
                radius: 8
                border.color: "#F4B400"
                border.width: 1
            }
        }

        RowLayout {
            spacing: 10
            Layout.fillWidth: true

            // ปุ่ม Login
            Control {
                id: loginButton
                Layout.fillWidth: true
                implicitHeight: 30
                background: Rectangle {

                    color: loginButton.hovered ? "#f6c02c" : "#F4B400"
                    radius: 8
                }

                contentItem: Label {
                    text: "Login"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    font.pixelSize: 14
                    color: "black"
                }

                MouseArea {
                    id: loginMouse
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor

                    //enabled: !loadingSpinner.running  // ✅ ป้องกันคลิกซ้ำ

                    onClicked: {
                        //loadingSpinner.visible = true;
                        //loadingSpinner.running = true;
                        errorLabel.visible = false;
                        loginHandler.login(usernameField.text, passwordField.text);
                    }
                }
            }

            // ปุ่ม Close
            Control {
                id: closeButton
                Layout.fillWidth: true
                implicitHeight: 30
                background: Rectangle {
                    color: closeButton.hovered ? "#f67c6f" : "#F45D4C"
                    radius: 8
                }

                contentItem: Label {
                    text: "Close"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    font.pixelSize: 14
                    color: "white"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: loginWindow.close()
                }
            }
        }

        RowLayout {
            id: versionRow
            spacing: 10  // 🔧 ปรับ spacing ให้เหมาะ เช่น 5–10 px
            anchors.horizontalCenter: parent.horizontalCenter  // ✅ ให้อยู่กึ่งกลาง

            Label {
                id: versionLabel
                text: ""
                color: "yellow"
                font.pixelSize: 12
                wrapMode: Text.Wrap
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Layout.alignment: Qt.AlignVCenter
            }

            Control {
                id: updateButton
                implicitWidth: 100  // ✅ กำหนดขนาดไม่ให้กว้างเกิน
                implicitHeight: 24
                visible: setUpdateAvailable  // ✅ ซ่อนปุ่มอัพเดตเริ่มต้น
                Layout.alignment: Qt.AlignVCenter

                background: Rectangle {
                    color: updateButton.hovered ? "#2b7328" : "#078f00"
                    radius: 8
                }

                contentItem: Label {
                    text: "Update Version"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                    font.pixelSize: 10
                    color: "white"
                    opacity: 1.0

                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        NumberAnimation {
                            from: 1.0
                            to: 0.3
                            duration: 500
                        }
                        NumberAnimation {
                            from: 0.3
                            to: 1.0
                            duration: 500
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: splashWindow.updateVersion()  // เรียกฟังก์ชันอัพเดตเวอร์ชัน
                }
            }
        }

        //BusyIndicator {
        //    id: loadingSpinner
        //    width: 32
        //    height: 32
        //    running: false
        //    visible: false
        //    Layout.alignment: Qt.AlignHCenter
        //}

        // ป้ายแสดงข้อผิดพลาด
        Label {
            id: errorLabel
            text: ""
            color: "yellow"
            visible: false
            wrapMode: Text.Wrap
            font.pixelSize: 10
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    // 🟤 Mercury
    Image {
        id: mercury
        source: "../../images/icons/mercury.png"
        width: 16
        height: 16
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: mercury
        duration: 3000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 60
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 60
                y: splash.height / 2
                radiusX: 60
                radiusY: 60
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 60
                y: splash.height / 2
                radiusX: 60
                radiusY: 60
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟤 Venus
    Image {
        id: venus
        source: "../../images/icons/venus.png"
        width: 20
        height: 20
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: venus
        duration: 5000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 90
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 90
                y: splash.height / 2
                radiusX: 90
                radiusY: 90
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 90
                y: splash.height / 2
                radiusX: 90
                radiusY: 90
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🌍 Earth
    Image {
        id: earth
        source: "../../images/icons/earth.png"
        width: 24
        height: 24
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: earth
        duration: 7000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 120
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 120
                y: splash.height / 2
                radiusX: 120
                radiusY: 120
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 120
                y: splash.height / 2
                radiusX: 120
                radiusY: 120
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🪐 Mars
    Image {
        id: mars
        source: "../../images/icons/mars.png"
        width: 22
        height: 22
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: mars
        duration: 8500
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 150
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 150
                y: splash.height / 2
                radiusX: 150
                radiusY: 150
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 150
                y: splash.height / 2
                radiusX: 150
                radiusY: 150
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟠 Jupiter
    Image {
        id: jupiter
        source: "../../images/icons/jupiter.png"
        width: 30
        height: 30
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: jupiter
        duration: 10000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 190
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 190
                y: splash.height / 2
                radiusX: 190
                radiusY: 190
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 190
                y: splash.height / 2
                radiusX: 190
                radiusY: 190
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟠 Saturn
    Image {
        id: saturn
        source: "../../images/icons/saturn.png"
        width: 30
        height: 30
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: saturn
        duration: 11000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 230
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 230
                y: splash.height / 2
                radiusX: 230
                radiusY: 230
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 230
                y: splash.height / 2
                radiusX: 230
                radiusY: 230
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟠 Uranus
    Image {
        id: uranus
        source: "../../images/icons/uranus.png"
        width: 26
        height: 26
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: uranus
        duration: 12500
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 270
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 270
                y: splash.height / 2
                radiusX: 270
                radiusY: 270
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 270
                y: splash.height / 2
                radiusX: 270
                radiusY: 270
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟠 Neptune
    Image {
        id: neptune
        source: "../../images/icons/neptune.png"
        width: 26
        height: 26
        opacity: 0.5  // ค่าระหว่าง 0.0 (โปร่งใสหมด) ถึง 1.0 (ทึบสนิท)
        z: 1
    }
    PathAnimation {
        target: neptune
        duration: 14000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 310
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 310
                y: splash.height / 2
                radiusX: 310
                radiusY: 310
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 310
                y: splash.height / 2
                radiusX: 310
                radiusY: 310
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    function hideSpinner() {
        loadingSpinner.visible = false;
        loadingSpinner.running = false;
    }

    function showError(msg) {
        errorLabel.text = msg;
        errorLabel.visible = true;
    }
}
