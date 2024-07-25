#!/usr/bin/env python3

import datetime
import os
from typing import Any, Dict, Union
from pathlib import Path
import json
import uuid
import config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ACTIVE_EXERCISES_DIR = "scenarios"
# script_dir = Path(__file__).parent / ACTIVE_EXERCISES_DIR
# EXERCISE_DIR = Path('/home/sami/git/SkillAegis') / ACTIVE_EXERCISES_DIR
EXERCISE_DIR = Path(config.exercise_directory)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scenarios = []
scenarioByUUID = {}
scenarioFilenameByUUID = {}
readErrors = {}


def read_exercise_dir():
    global scenarioFilenameByUUID, readErrors
    scenarioFilenameByUUID = {}
    readErrors = {}

    target_dir = EXERCISE_DIR
    json_files = target_dir.glob("*.json")
    exercises = []
    for json_file in list(json_files):
        with open(json_file) as f:
            try:
                parsed_exercise = json.load(f)
                exercises.append(parsed_exercise)
                uuid = parsed_exercise['exercise']['uuid']
                scenarioFilenameByUUID[uuid] = json_file
            except json.JSONDecodeError as e:
                relative_file = str(json_file.relative_to(EXERCISE_DIR))
                errorStr = f"json.JSONDecodeError: {e.msg}"
                f.seek(0)
                text = f.read()
                readErrors[relative_file] = {
                    'error': errorStr,
                    'text': text,
                }
                print(relative_file + ' - ' + errorStr)
    return exercises


def reloadJsonFiles():
    global scenarios, scenarioByUUID
    scenarios = read_exercise_dir()
    scenarioByUUID = { e['exercise']['uuid']: e for e in scenarios }

reloadJsonFiles()


def success(title: str, message: str = '', payload: dict = {}) -> dict:
    return {
        'success': True,
        'title': title,
        'message': message,
        'data': payload,
    }

def error(title: str, errorMessage: str, payload: dict = {}) -> dict:
    return {
        'success': False,
        'title': title,
        'message': errorMessage,
        'data': payload,
    }


def createScenario(newExercise) -> Union[dict, str]:
    global scenarios, scenarioByUUID
    today = datetime.date.today()
    exercise = {
        'name': newExercise.name,
        'namespace': newExercise.namespace,
        'description': newExercise.description,
        'meta': {},
        'uuid': str(uuid.uuid4()),
        'version': f"{today.year}{today.month}{today.day}",
    }
    inject_flow = []
    inject_payloads = []
    injects = []
    scenario = {
        'exercise': exercise,
        'inject_flow': inject_flow,
        'inject_payloads': inject_payloads,
        'injects': injects,
    }

    filename = "".join( x for x in newExercise.name if (x.isalnum() or x in "._- "))
    filename = f"{filename}.json"
    try:
        with open(EXERCISE_DIR / filename, 'w') as f:
            json.dump(scenario, f, indent=4)
    except Exception as e:
        print(e)
        return e
    
    scenarios.append(scenario)
    scenarioByUUID[exercise['uuid']] = scenario
    scenarioFilenameByUUID[exercise['uuid']] = EXERCISE_DIR / filename
    return scenario


def editScenario(updatedScenario) -> Union[dict, str]:
    global scenarios, scenarioByUUID, scenarioFilenameByUUID
    today = datetime.date.today()
    try:
        theUUID = updatedScenario.uuid
    except Exception:
        return 'Could not get UUID'
    scenario = scenarioByUUID[theUUID]
    scenario['exercise']['name'] = updatedScenario.name
    scenario['exercise']['namespace'] = updatedScenario.namespace
    scenario['exercise']['description'] = updatedScenario.description
    scenario['exercise']['version'] = f"{today.year}{today.month}{today.day}"
    scenario['exercise']['meta'] = updatedScenario.meta
    filename = scenarioFilenameByUUID[theUUID]
    try:
        with open(EXERCISE_DIR / filename, 'w') as f:
            json.dump(scenario, f, indent=4)
    except Exception as e:
        print(e)
        return e
    for i, sce in enumerate(scenarios):
        if sce['exercise']['uuid'] == scenario['exercise']['uuid']:
            scenarios[i] = scenario
    scenarioByUUID[theUUID] = scenario
    return scenario


def deleteScenario(uuid: str) -> Union[bool, str]:
    global scenarios, scenarioByUUID

    if uuid in scenarioFilenameByUUID:
        try:
            os.remove(scenarioFilenameByUUID[uuid])
        except Exception as e:
            print(e)
            return e
        del scenarioByUUID[uuid]
        scenarios = [s for s in scenarios if s['exercise']['uuid'] != uuid]
        return True
    return 'Scenario not found'


def saveInject(scenario_uuid: str, injectToSave, injectFlowToSave) -> Union[dict, str]:
    global scenarios, scenarioByUUID

    if scenario_uuid not in scenarioByUUID:
        return 'Invalid scenario'
    scenario = scenarioByUUID[scenario_uuid]

    # Search inject in scenario and create/update it
    injectToSave = injectToSave.dict()
    found = False
    for i, inject in enumerate(scenario['injects']):
        if inject['uuid'] == injectToSave['uuid']:
            scenario['injects'][i] = injectToSave
            found = True
    if not found:
        scenario['injects'].append(injectToSave)

    injectFlowToSave = injectFlowToSave.dict()
    for i, injectF in enumerate(scenario['inject_flow']):
        if injectF['inject_uuid'] == injectFlowToSave['inject_uuid']:
            scenario['inject_flow'][i] = injectFlowToSave
            found = True
    if not found:
        scenario['inject_flow'].append(injectFlowToSave)

    saveResult = saveScenario(scenario_uuid, scenario)
    return saveResult


def saveScenario(scenario_uuid: str, scenario: dict) -> Union[bool, str]:
    global scenarioFilenameByUUID
    filename = scenarioFilenameByUUID[scenario_uuid]
    try:
        with open(EXERCISE_DIR / filename, 'w') as f:
            json.dump(scenario, f, indent=4)
    except Exception as e:
        print(e)
        return e
    return True


def removeInject(scenario_uuid: str, inject_uuid: str) -> Union[bool, str]:
    global scenarios, scenarioByUUID

    if scenario_uuid not in scenarioByUUID:
        return 'Invalid scenario'
    scenario = scenarioByUUID[scenario_uuid]

    for i, inject in enumerate(scenario['injects']):
        if inject['uuid'] == inject_uuid:
            scenario['injects'].pop(i)
    
    for i, injectF in enumerate(scenario['inject_flow']):
        if injectF['inject_uuid'] == inject_uuid:
            scenario['inject_flow'].pop(i)

    saveResult = saveScenario(scenario_uuid, scenario)
    return saveResult


def orderInjects(scenario_uuid, inject_uuids) -> Union[bool, str]:
    global scenarios, scenarioByUUID

    if scenario_uuid not in scenarioByUUID:
        return 'Invalid scenario'
    scenario = scenarioByUUID[scenario_uuid]

    orderedInjects = []
    orderedInjectFlows = []
    for inject_uuid in inject_uuids:
        inject = [i for i in scenario['injects'] if i['uuid'] == inject_uuid][0]
        injectFlow = [i for i in scenario['inject_flow'] if i['inject_uuid'] == inject_uuid][0]
        orderedInjects.append(inject)
        orderedInjectFlows.append(injectFlow)
    
    scenario['injects'] = orderedInjects
    scenario['inject_flow'] = orderedInjectFlows

    saveResult = saveScenario(scenario_uuid, scenario)
    return saveResult


class Exercise(BaseModel):
    name: str
    namespace: str
    description: str | None = None
    uuid: str | None = None
    version: str | None = None
    meta: dict | None = {}


class Inject(BaseModel):
    name: str
    action: str
    target_tool: str | None = None
    uuid: str | None = None
    description: str | None = None
    inject_evaluation: list | None = []


class InjectFlow(BaseModel):
    inject_uuid: str
    description: str | None = None
    requirements: dict | None = None
    sequence: dict | None = None


class InjectOrder(BaseModel):
    inject_uuids: list


@app.get("/scenarios/index")
def scenarios_index():
    global scenarios, scenarioByUUID, readErrors
    return {
        'scenarios': scenarios,
        'scenario_by_uuid': scenarioByUUID,
        'read_errors': readErrors,
    }


@app.post("/scenarios/reload")
def scenarios_reload():
    global scenarios, scenarioByUUID, readErrors
    reloadJsonFiles()
    return {
        'scenarios': scenarios,
        'scenario_by_uuid': scenarioByUUID,
        'read_errors': readErrors,
    }


@app.get("/scenarios/view/{uuid}")
def scenarios_view(uuid: str):
    scenario = scenarioByUUID.get(uuid, None)
    if scenario is not None:
        return scenario
    return error('Scenario not found', uuid)


@app.post("/scenarios/add")
def scenarios_add(exercise: Exercise):
    scenario = createScenario(exercise)
    if type(scenario) is dict:
        return success('New scenario created', payload=scenario)
    return error('Could not create scenario', scenario)


@app.post("/scenarios/edit")
def scenarios_edit(exercise: Exercise):
    scenario = editScenario(exercise)
    if type(scenario) is dict:
        return success('Scenario Updated', payload=scenario)
    return error('Could not update scenario', scenario)


@app.post("/scenarios/delete/{uuid}")
def scenarios_delete(uuid: str):
    result = deleteScenario(uuid)
    if result is True:
        return success(f"Scenario deleted")
    return error('Could not delete scenario', result)


@app.post("/scenarios/save-inject/{scenario_uuid}")
def save_inject(scenario_uuid: str, inject: Inject, injectFlow: InjectFlow):
    result = saveInject(scenario_uuid, inject, injectFlow)
    if result is True:
        return success(f"Inject saved")
    return error('Could not save inject', result)


@app.post("/scenarios/delete-inject/{scenario_uuid}/{inject_uuid}")
def save_inject(scenario_uuid: str, inject_uuid: str):
    result = removeInject(scenario_uuid, inject_uuid)
    if result is True:
        return success(f"Inject removed")
    return error('Could not remove inject', result)


@app.post("/scenarios/order-inject/{scenario_uuid}")
def save_inject(scenario_uuid: str, injectOrder: InjectOrder):
    result = orderInjects(scenario_uuid, injectOrder.inject_uuids)
    if result is True:
        return success(f"Injects reordered")
    return error('Could not reorder injects', result)


app.mount('/', StaticFiles(directory='dist', html=True))