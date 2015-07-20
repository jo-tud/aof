var BpmnModeler = window.BpmnJS;

var container = $('#js-drop-zone');

var canvas = $('#js-canvas');

var renderer = new BpmnModeler({ container: canvas });

var diagramURL = '/api/app-ensembles/'+ae_uri+'/bpmn';
console.log("Diagram URL: " + diagramURL);

function createNewDiagram() {
    $.get(diagramURL, function (data) {
        xmlString = xmlString = (new XMLSerializer()).serializeToString(data);
        openDiagram(xmlString);
    });
}

function openDiagram(xml) {

    renderer.importXML(xml, function (err) {

        if (err) {
            console.log("An error occured.")
            container
                .removeClass('with-diagram')
                .addClass('with-error');

            container.find('.error pre').text(err.message);

            console.error(err);
        } else {
            container
                .removeClass('with-error')
                .addClass('with-diagram');
        }


    });
}

function saveSVG(done) {
    renderer.saveSVG(done);
}

function saveDiagram(done) {

    renderer.saveXML({ format: true }, function (err, xml) {
        done(err, xml);
    });
}

// bootstrap diagram functions

$(document).on('ready', function () {

    createNewDiagram();

});