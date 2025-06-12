// ZoomableImage.qml
import QtQuick

Rectangle {
    id: surfaceView
    property url imagePath: ""
    property int imageWidth: 1103
    property int imageHeight: 768
    property real zoom: 1.0
    property point offset: Qt.point(0, 0)
    property point zoomCenter: Qt.point(width / 2, height / 2)

    color: "#e3f2fd"
    clip: true
    radius: 8
    anchors.fill: parent

    Image {
        id: zoomableImage
        source: imagePath
        width: imageWidth
        height: imageHeight
        fillMode: Image.Pad
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

        onPressed: {
            lastPos = Qt.point(mouse.x, mouse.y);
            cursorShape = Qt.ClosedHandCursor;
        }

        onReleased: cursorShape = Qt.ArrowCursor

        onPositionChanged: {
            surfaceView.zoomCenter = Qt.point(mouse.x, mouse.y);
            if (mouse.buttons & Qt.LeftButton) {
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
            const pos = Qt.point(wheel.x, wheel.y);

            const dx = (pos.x - surfaceView.offset.x) / oldZoom;
            const dy = (pos.y - surfaceView.offset.y) / oldZoom;
            surfaceView.offset.x = pos.x - dx * newZoom;
            surfaceView.offset.y = pos.y - dy * newZoom;
            surfaceView.zoom = newZoom;
            surfaceView.zoomCenter = pos;
        }
    }
}
