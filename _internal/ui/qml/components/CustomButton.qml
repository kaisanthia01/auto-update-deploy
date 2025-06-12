// ui/qml/components/CustomButton.qml

import QtQuick 2.15
import QtQuick.Controls 2.15

Control {
    id: root
    property color bgColor: "#F4B400"
    property string label: "Button"

    implicitWidth: 200
    implicitHeight: 42

    background: Rectangle {
        color: root.bgColor
        radius: 8
    }

    contentItem: Text {
        text: root.label
        anchors.centerIn: parent
        color: "black"
        font.pixelSize: 16
        font.bold: true
    }
}
