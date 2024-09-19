
import { computed, reactive } from 'vue'

export const store = reactive({
    selected_scenario: null,
    scenarios: [],
    scenario_validated_by_uuid: [],
    scenario_filename_by_uuid: [],
    read_errors: [],
    cexf_schema: {},
})

export const scenarioByUUID = computed(() => {
    const scenariosByUUID = {}
    store.scenarios.forEach((scenario) => {
        scenariosByUUID[scenario.exercise.uuid] = scenario
    })
    return scenariosByUUID || {}
})

export const selectedScenario = computed(() => {
    return scenarioByUUID.value[store.selected_scenario] || null
})

export const selectedScenarioUUID = computed(() => {
    return store.selected_scenario || null
})
export function hasScenario() {
    return scenarioByUUID.value[store.selected_scenario] !== undefined
}
export function hasScenarios() {
    return store.scenarios.length > 0
}

export function addNewInjectToSelectedScenario(inject, injectFlow) {
    scenarioByUUID.value[store.selected_scenario].injects.push(inject)
    scenarioByUUID.value[store.selected_scenario].inject_flow.push(injectFlow)
}

export function updateInjectToSelectedScenario(injectToUpdate, injectFlowToUpdate) {
    scenarioByUUID.value[store.selected_scenario].injects = scenarioByUUID.value[store.selected_scenario].injects.map((inject) => {
        return inject.uuid == injectToUpdate.uuid ? injectToUpdate : inject
    })
    scenarioByUUID.value[store.selected_scenario].inject_flow = scenarioByUUID.value[store.selected_scenario].inject_flow.map((injectFlow) => {
        return injectFlow.inject_uuid == injectFlowToUpdate.inject_uuid ? injectFlowToUpdate : injectFlow
    })
}

export function removeInjectFromSelectedScenario(inject_uuid) {
    scenarioByUUID.value[store.selected_scenario].injects = scenarioByUUID.value[store.selected_scenario].injects.filter((inj) => inj.uuid != inject_uuid)
    scenarioByUUID.value[store.selected_scenario].inject_flow = scenarioByUUID.value[store.selected_scenario].inject_flow.filter((inj) => inj.inject_uuid != inject_uuid)

    // Remove any inject requirements that existed for that inject
    for (let i = 0; i < scenarioByUUID.value[store.selected_scenario].inject_flow.length; i++) {
        const injectF = scenarioByUUID.value[store.selected_scenario].inject_flow[i];
        if (injectF?.requirements?.inject_uuid == inject_uuid) {
            injectF.requirements = {}
        }
    }
}