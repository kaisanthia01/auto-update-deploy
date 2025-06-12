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

    // 🪐 Canvas สำหรับเส้นวงโคจร (อยู่หลัง)
    Canvas {
        id: orbitCanvas
        anchors.fill: parent
        z: 0
        onPaint: {
            let ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = "#334a80";
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            let cx = width / 2;
            let cy = height / 2;

            // รัศมีวงโคจร
            [60, 90, 130, 170].forEach(radius => {
                ctx.beginPath();
                ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
                ctx.stroke();
            });
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

        Text {
            id: statusText
            text: splashBridge.message
            color: "yellow"
            font.pixelSize: 14
            font.bold: true
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }
    }

    // 🌍 Earth
    Image {
        id: earth
        source: "../../images/icons/earth.png"
        width: 30
        height: 30
        z: 1
    }
    PathAnimation {
        target: earth
        duration: 7000
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

    // 🪐 Mars
    Image {
        id: mars
        source: "../../images/icons/jupiter.png"
        width: 26
        height: 26
        z: 1
    }
    PathAnimation {
        target: mars
        duration: 9000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 130
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 130
                y: splash.height / 2
                radiusX: 130
                radiusY: 130
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 130
                y: splash.height / 2
                radiusX: 130
                radiusY: 130
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟠 Venus
    Image {
        id: venus
        source: "../../images/icons/sun.png"
        width: 24
        height: 24
        z: 1
    }
    PathAnimation {
        target: venus
        duration: 5000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 70
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 70
                y: splash.height / 2
                radiusX: 70
                radiusY: 70
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 70
                y: splash.height / 2
                radiusX: 70
                radiusY: 70
                direction: PathArc.Clockwise
            }
        }
        running: true
    }

    // 🟤 Mercury
    Image {
        id: mercury
        source: "../../images/icons/mercury.png"
        width: 18
        height: 18
        z: 1
    }
    PathAnimation {
        target: mercury
        duration: 4000
        loops: Animation.Infinite
        path: Path {
            startX: splash.width / 2 + 45
            startY: splash.height / 2
            PathArc {
                x: splash.width / 2 - 45
                y: splash.height / 2
                radiusX: 45
                radiusY: 45
                direction: PathArc.Clockwise
            }
            PathArc {
                x: splash.width / 2 + 45
                y: splash.height / 2
                radiusX: 45
                radiusY: 45
                direction: PathArc.Clockwise
            }
        }
        running: true
    }
}
