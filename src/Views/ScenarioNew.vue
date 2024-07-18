<script setup>
import { addScenario, fetchScenarios } from '@/api.js'
import { ajaxFeedback } from '@/main.js'
import { store } from '@/store'
import { faSave, faTimes } from '@fortawesome/free-solid-svg-icons'
import { computed, watch, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const canBeSaved = computed(() => {
  return exercise_name.value.length >= 3 && exercise_namespace.value.length >= 2
})
const exercise_name = ref('')
const exercise_namespace = ref('')

async function createScenario() {
  const result = await addScenario({
    name: exercise_name.value,
    namespace: exercise_namespace.value
  })
  const scenarioUUID = result.data.exercise.uuid
  store.selected_scenario = scenarioUUID
  ajaxFeedback(result)
  fetchScenarios()
  nextTick(() => {
    router.push({ name: 'Scenario Overview', params: { uuid: scenarioUUID } })
  })
}

function cancel() {
  router.push({ name: 'Scenario Index' })
}

watch(
  () => route.path,
  () => {
    exercise_name.value = ''
    exercise_namespace.value = ''
  }
),
  { immediate: true }
</script>

<template>
  <div>
    <div>
      <div class="mb-4 flex flex-row-reverse gap-2">
        <button
          class="btn btn-success select-none"
          @click="createScenario()"
          :disabled="!canBeSaved"
        >
          <FontAwesomeIcon :icon="faSave" class="fa-fw"></FontAwesomeIcon>Create Scenario
        </button>
        <button class="btn btn-danger select-none" @click="cancel()">
          <FontAwesomeIcon :icon="faTimes" class="fa-fw"></FontAwesomeIcon>Cancel
        </button>
      </div>

      <form>
        <div class="flex flex-col gap-6">
          <div class="flex flex-row gap-6">
            <div class="basis-1/2">
              <label for="name" class="block text-gray-700 font-bold mb-2">Scenario Name</label>
              <input
                type="text"
                v-model="exercise_name"
                class="shadow border w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border-slate-400"
                id="name"
                placeholder="My Scenario"
                autofocus
              />
            </div>

            <div>
              <label for="namespace" class="block text-gray-700 font-bold mb-2"
                >Scenario Namespace</label
              >
              <input
                type="text"
                v-model="exercise_namespace"
                class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                id="namespace"
                placeholder="My Namespace"
              />
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
