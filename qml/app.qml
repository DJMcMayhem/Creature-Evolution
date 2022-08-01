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

    minimumWidth: 800
    minimumHeight: 900

    visible: true

    Rectangle {
        id: simulationBox

        width: 700
        height: 700
        anchors.centerIn: parent

        border.color: "black"
        border.width: 5

        Environment {
            id: environment

            x: 5
            y: 5
            width: parent.width - x * 2
            height: parent.height - y * 2
            MouseArea {
                anchors.fill: parent
                onClicked: environment.on_clicked(mouse.x, mouse.y)
            }
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
            text: "Prey Count: " + environment.prey_count
        }

        Text {
            text: "Predator Count: " + environment.predator_count
        }
    }
}
