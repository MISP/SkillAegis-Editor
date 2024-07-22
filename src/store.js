
import { computed, reactive } from 'vue'

export const store = reactive({
    selected_scenario: null,
    scenarios: [],
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
export function hasScenario(uuid) {
    return scenarioByUUID.value[store.selected_scenario] !== undefined
}
export function hasScenarios() {
    return store.scenarios.length > 0
}

export function addNewInjectToSelectedScenario(inject, injectFlow) {
    scenarioByUUID.value[store.selected_scenario].injects.push(inject)
    scenarioByUUID.value[store.selected_scenario].inject_flow.push(injectFlow)
}