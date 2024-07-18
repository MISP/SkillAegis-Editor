#!/usr/bin/env python3

import datetime
import os
from typing import Any, Dict, Union
from pathlib import Path
import json
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ACTIVE_EXERCISES_DIR = "active_exercises"
script_dir = Path(__file__).parent / ACTIVE_EXERCISES_DIR
EXERCISE_DIR = Path('/home/sami/git/exercise-dashboard') / ACTIVE_EXERCISES_DIR

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


def read_exercise_dir():
    global scenarioFilenameByUUID
    scenarioFilenameByUUID = {}

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
                print(e)
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
            json.dump(scenario, f)
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
            json.dump(scenario, f)
    except Exception as e:
        print(e)
        return e
    for i, sce in enumerate(scenarios):
        if sce['exercise']['uuid'] == scenario['exercise']['uuid']:
            scenarios[i] = scenario
    scenarioByUUID[theUUID] = scenario
    return scenario


def deleteScenario(uuid: str):
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

class Exercise(BaseModel):
    name: str
    namespace: str
    description: str | None = None
    uuid: str | None = None
    version: str | None = None
    meta: dict | None = {}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/scenarios/index")
def scenarios_index():
    global scenarios
    return {
        'scenarios': scenarios,
        'scenario_by_uuid': scenarioByUUID,
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

