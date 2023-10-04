import argparse

import xml.etree.ElementTree as ET

from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.general import User
from diagrams.aws.network import ELB
from diagrams.azure.general import Quickstartcenter
from diagrams.azure.general import Azurehome
from diagrams.azure.analytics import DataLakeAnalytics
from diagrams.onprem.network import Internet
from diagrams.azure.compute import CloudServices
from diagrams.azure.ml import MachineLearningStudioWebServicePlans
from diagrams.onprem.database import Mongodb

def icon(element):
    if 'serviceTask' in element.tag:
        if '{http://activiti.org/bpmn}delegateExpression' in element.attrib:
            if element.attrib['{http://activiti.org/bpmn}delegateExpression'] == '${httpRequestorTask}':
                return Internet(element.attrib['id'])
            elif element.attrib['{http://activiti.org/bpmn}delegateExpression'] in ['${updateScimUserTask}', '${createScimUserTask}']:
                return Mongodb(element.attrib['id'])
        return EC2(element.attrib['id'])
    elif 'userTask' in element.tag:
        return User(element.attrib['id'])
    elif 'exclusiveGateway' in element.tag:
        return ELB(element.attrib['id'])
    elif 'startEvent' in element.tag:
        return Quickstartcenter(element.attrib['id'])
    elif 'endEvent' in element.tag:
        return Azurehome(element.attrib['id'])
    elif 'scriptTask' in element.tag:
        return CloudServices(element.attrib['id'])
    elif 'boundaryEvent' in element.tag:
        return MachineLearningStudioWebServicePlans(element.attrib['id'])
    else:
        return DataLakeAnalytics(element.attrib['id'])
    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bpmn')
    parser.add_argument('direction', nargs='?', default='TB')
    args = parser.parse_args()

    args.direction = args.direction.upper()
    if args.direction not in ['TB', 'BT', 'LR', 'RL']:
        print(
            f'Invalid direction param {args.direction} reverting to default, "TB"')
        args.direction = 'TB'

    tree = None

    with open(args.bpmn) as file:
        tree = ET.parse(file)

    root = tree.getroot()
    name = root[0].attrib['id']

    path = {}

    with Diagram(name, direction=args.direction):
        for element in root[0]:
            if 'id' in element.attrib and 'sequenceFlow' not in element.tag:
                if element.attrib['id'] not in path:
                    path[element.attrib['id']] = {}
                    path[element.attrib['id']]['node'] = icon(element)
                    path[element.attrib['id']]['target'] = []
                    if 'attachedToRef' in element.attrib:
                        path[element.attrib['attachedToRef']]['target'].append(
                            element.attrib['id'])
        for element in root[0]:
            if 'sourceRef' in element.attrib:
                path[element.attrib['sourceRef']]['target'].append(
                    element.attrib['targetRef'])
        for node in path:
            for target in path[node]['target']:
                try:
                    path[node]['node'] >> path[target]['node']
                except Exception as e:
                    print(e)
