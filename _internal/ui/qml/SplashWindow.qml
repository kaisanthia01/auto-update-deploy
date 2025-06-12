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
            [60, 90, 120, 150, 190, 230, 270, 310].forEach(radius => {
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

    // 🟤 Mercury
    Image {
        id: mercury
        source: "../../images/icons/mercury.png"
        width: 16
        height: 16
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
}
