// File: ui/qml/SolarSystem.qml

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Shapes 1.15

Rectangle {
    id: root
    width: 800
    height: 800
    color: "#000c1f"

    // จุดศูนย์กลางระบบสุริยะ: ดวงอาทิตย์ (ใช้โลโก้ของคุณ)
    Image {
        id: sun
        source: "../../images/icons/logowxao-6.png"
        width: 80
        height: 80
        anchors.centerIn: parent
        z: 2
    }

    // ✅ Canvas วาดเส้นวงโคจร (เส้นลายวงกลม)
    Canvas {
        id: orbitCanvas
        anchors.fill: parent
        z: 0
        onPaint: {
            const ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = "#334a80";
            ctx.setLineDash([4, 4]);
            ctx.lineWidth = 1;

            const cx = width / 2;
            const cy = height / 2;
            const radii = [60, 90, 120, 150, 190, 230, 270, 310];

            for (let r of radii) {
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, 2 * Math.PI);
                ctx.stroke();
            }
        }
        Component.onCompleted: requestPaint()
    }

    // 🔄 สร้างดาวโคจรแบบซ้ำได้ด้วย Component + Repeater
    Component {
        id: orbitingPlanet
        Item {
            required property string name
            required property string image
            required property real radius
            required property int size
            required property int duration

            Image {
                id: planet
                source: image
                width: size
                height: size
                z: 1
            }

            PathAnimation {
                target: planet
                duration: duration
                loops: Animation.Infinite
                path: Path {
                    startX: root.width / 2 + radius
                    startY: root.height / 2
                    PathArc {
                        x: root.width / 2 - radius
                        y: root.height / 2
                        radiusX: radius
                        radiusY: radius
                        direction: PathArc.Clockwise
                    }
                    PathArc {
                        x: root.width / 2 + radius
                        y: root.height / 2
                        radiusX: radius
                        radiusY: radius
                        direction: PathArc.Clockwise
                    }
                }
                running: true
            }
        }
    }

    // 🪐 รายชื่อดาวในระบบสุริยะ
    ListModel {
        id: planetModel
        ListElement {
            name: "Mercury"
            image: "../../images/mercury.png"
            radius: 60
            size: 16
            duration: 3000
        }
        ListElement {
            name: "Venus"
            image: "../../images/venus.png"
            radius: 90
            size: 20
            duration: 5000
        }
        ListElement {
            name: "Earth"
            image: "../../images/earth.png"
            radius: 120
            size: 24
            duration: 7000
        }
        ListElement {
            name: "Mars"
            image: "../../images/mars.png"
            radius: 150
            size: 22
            duration: 8500
        }
        ListElement {
            name: "Jupiter"
            image: "../../images/jupiter.png"
            radius: 190
            size: 30
            duration: 10000
        }
        ListElement {
            name: "Saturn"
            image: "../../images/saturn.png"
            radius: 230
            size: 30
            duration: 11000
        }
        ListElement {
            name: "Uranus"
            image: "../../images/uranus.png"
            radius: 270
            size: 26
            duration: 12500
        }
        ListElement {
            name: "Neptune"
            image: "../../images/neptune.png"
            radius: 310
            size: 26
            duration: 14000
        }
    }

    // 🔁 สร้างดาวทุกดวง
    Repeater {
        model: planetModel
        delegate: orbitingPlanet
    }

    // 🌟 ชื่อโปรแกรม
    Column {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 20
        spacing: 6
        z: 3

        Text {
            text: "☀ AWSS Solar Orbit Simulation"
            color: "white"
            font.pixelSize: 20
            font.bold: true
        }
    }
}
