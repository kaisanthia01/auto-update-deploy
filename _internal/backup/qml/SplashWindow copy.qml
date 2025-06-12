// ui/qml/splash.qml

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: splash
    width: 380
    height: 420
    color: "#1b2a4b"
    radius: 12
    opacity: 0.0

    // ✅ Fade-in animation
    Behavior on opacity {
        NumberAnimation {
            duration: 250
            easing.type: Easing.InOutQuad
        }
    }

    Component.onCompleted: {
        opacity = 1.0;
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        Image {
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
}
