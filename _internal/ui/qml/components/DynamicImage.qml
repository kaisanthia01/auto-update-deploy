import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: dynamicImage
    property alias imageId: imageItem

    // === External Properties ===
    property string fallbackSource: ""
    property string dynamicSource: ""
    property bool useDynamic: false

    // === Internal State ===
    property string effectiveSource: useDynamic && dynamicSource !== "" ? dynamicSource : fallbackSource

    signal imageStatusChanged(int status)

    Image {
        id: imageItem
        anchors.fill: parent
        source: effectiveSource
        fillMode: Image.PreserveAspectFit
        smooth: true
        asynchronous: true
        cache: false   // ✅ ต้องใส่ไว้เพื่อให้โหลดภาพใหม่ทุกครั้งที่เปลี่ยน source
        opacity: 0.0

        onStatusChanged: {
            console.log("🖼 DynamicImage status:", status, "URL:", source);
            imageStatusChanged(status);
            if (status === Image.Ready) {
                imageItem.opacity = 1.0;
            } else {
                imageItem.opacity = 0.0;
            }
        }

        Behavior on opacity {
            NumberAnimation {
                duration: 250
                easing.type: Easing.InOutQuad
            }
        }
    }
} 
