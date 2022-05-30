import argparse

import xml.etree.ElementTree as ET

from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.general import User
from diagrams.aws.network import ELB
from diagrams.azure.general import Quickstartcenter
from diagrams.azure.general import Azurehome
from diagrams.azure.analytics import DataLakeAnalytics

parser = argparse.ArgumentParser()
parser.add_argument('bpmn')
args = parser.parse_args()

tree = None

with open(args.bpmn) as file:
    tree = ET.parse(file)

root = tree.getroot()
name = root[0].attrib['id']

path = {}


def icon(element):
    if 'serviceTask' in element.tag:
        return EC2(element.attrib['id'])
    elif 'userTask' in element.tag:
        return User(element.attrib['id'])
    elif 'exclusiveGateway' in element.tag:
        return ELB(element.attrib['id'])
    elif 'startEvent' in element.tag:
        return Quickstartcenter(element.attrib['id'])
    elif 'endEvent' in element.tag:
        return Azurehome(element.attrib['id'])
    else:
        return DataLakeAnalytics(element.attrib['id'])


with Diagram(name, direction='LR'):
    for element in root[0]:
        if 'id' in element.attrib and 'sequenceFlow' not in element.tag:
            if element.attrib['id'] not in path:
                path[element.attrib['id']] = {}
                path[element.attrib['id']]['node'] = icon(element)
                path[element.attrib['id']]['target'] = []
                if 'attachedToRef' in element.attrib:
                    path[element.attrib['attachedToRef']]['target'].append(
                        element.attrib['id'])
        elif 'sourceRef' in element.attrib:
            path[element.attrib['sourceRef']]['target'].append(
                element.attrib['targetRef'])
    for node in path:
        for target in path[node]['target']:
            try:
                path[node]['node'] >> path[target]['node']
            except Exception as e:
                print(e)
