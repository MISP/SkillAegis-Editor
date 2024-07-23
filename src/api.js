import { reactive, computed } from "vue";
import { store } from '@/store.js'

const URL = process.env.NODE_ENV === "production" ? undefined : "http://localhost:5000";

const endpoints = {
    'scenarios-index': '/scenarios/index',
    'scenarios-view': '/scenarios/view',
    'scenarios-add': '/scenarios/add',
    'scenarios-edit': '/scenarios/edit',
    'scenarios-delete': '/scenarios/delete',
    'inject-save': '/scenarios/save-inject',
    'inject-delete': '/scenarios/delete-inject',
}

async function get(url) {
    url = URL + url
    const options = {
        method: "GET",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        },
    }

    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    return json
}

async function post(url, payload) {
    url = URL + url
    const options = {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json;charset=UTF-8",
        },
        body: JSON.stringify(payload),
    }
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    return json
}

export async function fetchScenarios() {
    const data = await get(endpoints['scenarios-index'])
    store.scenarios = data.scenarios
}

export async function fetchScenario() {
    return await get(endpoints['scenarios-view'])
}

export async function addScenario(payload) {
    return await post(endpoints['scenarios-add'], payload)
}

export async function editScenario(payload) {
    const url = endpoints['scenarios-edit']
    return await post(url, payload)
}

export async function deleteScenario(uuid) {
    const url = endpoints['scenarios-delete'] + `/${uuid}`
    const data = await post(url)
    if (data.success) {
        store.scenarios = store.scenarios.filter((s) => s.exercise.uuid != uuid)
    }
    return data
}

export async function saveInject(scenario_uuid, inject, injectFlow) {
    const url = endpoints['inject-save'] + `/${scenario_uuid}`
    const payload = {
        inject: inject,
        injectFlow: injectFlow,
    }
    return await post(url, payload)
}
export async function removeInject(scenario_uuid, inject_uuid) {
    const url = endpoints['inject-delete'] + `/${scenario_uuid}/${inject_uuid}`
    const payload = {
    }
    return await post(url, payload)
}