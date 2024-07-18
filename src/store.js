
import { computed, reactive } from 'vue'

export const store = reactive({
    selected_scenario: null,
    scenarios: [],
    scenario_by_uuid: {},
})

export const selectedScenario = computed(() => {
    return store.scenario_by_uuid[store.selected_scenario] || null
})

export const selectedScenarioUUID = computed(() => {
    return store.selected_scenario || null
})
export function hasScenario(uuid) {
    return store.scenario_by_uuid[store.selected_scenario] !== undefined
}
export function hasScenarios() {
    return store.scenarios.length > 0
}