// ui/qml/LoginWindow.qml

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
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

    // 🖱️ รองรับ mouse drag ที่จัดการฝั่ง Python
    MouseArea {
        anchors.fill: parent
        drag.target: null
        cursorShape: Qt.OpenHandCursor
        propagateComposedEvents: true
        onPressed: mouse.accepted = false  // ให้ event ส่งไปฝั่ง Python
        onPositionChanged: mouse.accepted = false
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 30
        spacing: 2.5

        Image {
            source: "../../images/icons/logowxao-6.png"
            width: 110
            height: 110
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
        }

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

            Control {
                Layout.fillWidth: true
                implicitHeight: 30
                background: Rectangle {
                    color: "#F4B400"
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

                    enabled: !loadingSpinner.running  // ✅ ป้องกันคลิกซ้ำ

                    onClicked: {
                        loadingSpinner.visible = true;
                        loadingSpinner.running = true;
                        errorLabel.visible = false;
                        loginHandler.login(usernameField.text, passwordField.text);
                    }
                }
            }

            Control {
                Layout.fillWidth: true
                implicitHeight: 30
                background: Rectangle {
                    color: "#F45D4C"
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

        BusyIndicator {
            id: loadingSpinner
            width: 32
            height: 32
            running: false
            visible: false
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            id: errorLabel
            text: ""
            color: "yellow"
            visible: false
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
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
