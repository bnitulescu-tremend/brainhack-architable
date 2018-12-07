# generates Archie file
def generateArchiFile(boxes, lines, outputFileName):
    file = open(outputFileName, "w")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:archimate="http://www.archimatetool.com/archimate" name="Archie" id="09bc0fa0-63a8-4c4c-8c01-2a0fc803dde2" version="4.0.1">\n')

    # generate boxes
    file.write('<folder name="Application" id="d3356268-2385-4e27-b7fc-910ace026fa5" type="application">\n')

    for b in boxes:
        file.write('    <element xsi:type="archimate:ApplicationService" name="' + b.text + '" id="AppElem' + str(b.id) + '"/>\n')

    file.write('</folder>\n')

    # generate relationships
    file.write('<folder name="Relations" id="637ec326-b7ad-4550-bea2-ea7b6f7b8cab" type="relations">\n')

    for l in lines:
        file.write('    <element xsi:type="archimate:ServingRelationship" id="Relation' +
                   str(l.boxes[0]) + '-' + str(l.boxes[1]) +
                   '" source="AppElem' + str(l.boxes[0]) + '" target="AppElem' + str(l.boxes[1]) + '"/>\n')

    file.write('</folder>\n')

    file.write('<folder name="Views" id="4f118b5c-63da-45d3-b3c6-7dd9c43cfae9" type="diagrams">\n')
    file.write('    <element xsi:type="archimate:ArchimateDiagramModel" name="Default View" id="4303c01b-aeab-49ab-96dd-bf87beb79006">\n')

    for b in boxes:
        # look for target connections
        targetConn = ""
        for l in lines:
            if(l.boxes[1] == b.id):
                targetConn = targetConn + 'Conn' + str(l.boxes[0]) + '-' + str(l.boxes[1]) + ' '

        if(targetConn != ""):
            targetConn = '  targetConnections="' + targetConn.strip(' ') + '"'

        file.write('        <child xsi:type="archimate:DiagramObject" id="ViewChild' + str(b.id) + '" ' +
                    'archimateElement="AppElem' + str(b.id) + '"' + targetConn + '>\n')
        file.write('            <bounds x="' + str(b.box[0]) + '" y="' + str(b.box[1]) + '" width="' + str(b.box[2]) + '" height="' + str(b.box[3]) + '"/>\n')

        for l in lines:
            if(l.boxes[0] == b.id):
                file.write('            <sourceConnection xsi:type="archimate:Connection" id="Conn' + str(l.boxes[0]) + '-'  + str(l.boxes[1]) + '" ' +
                           'source="ViewChild' + str(l.boxes[0]) + '" ' +
                           'target="ViewChild' + str(l.boxes[1]) + '" ' +
                           'archimateRelationship="Relation' + str(l.boxes[0]) + '-'  + str(l.boxes[1]) + '"/>\n')


        file.write('        </child>\n')

    file.write('    </element>\n')
    file.write('</folder>\n')

    file.write('</archimate:model>\n')

    file.close()
