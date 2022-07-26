import QtQuick 2.6
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Material 2.0
import QtGraphicalEffects 1.15
import QtQuick.Controls.Universal 2.0
import Qt.labs.settings 1.0

import Environment 1.0

ApplicationWindow {
    id: window

    minimumWidth: 600
    minimumHeight: 600

    visible: true

    Rectangle {
        id: simulationBox

        width: 500
        height: 500
        anchors.centerIn: parent

        border.color: "black"
        border.width: 5

        Environment {
            id: environment

            x: 5
            y: 5
            width: parent.width - x * 2
            height: parent.height - y * 2
        }
    }

    Column {
        anchors.top: simulationBox.bottom
        anchors.left: simulationBox.left
        anchors.topMargin: 5

        spacing: 5

        Text {
            text: "FPS: " + environment.fps
        }

        Text {
            text: "Actor Count: " + environment.actor_count
        }
    }
}
