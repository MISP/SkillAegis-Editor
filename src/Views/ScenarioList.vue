<script setup>
import { store } from '@/store.js'
import { ref, watch, onUpdated, onBeforeMount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ajaxFeedback, toast } from '@/main.js'
import { deleteScenario as doDeleteScenario, fetchScenarios } from '@/api.js'
import {
  faWarning,
  faHashtag,
  faSpinner,
  faEdit,
  faTrash,
  faPlus
} from '@fortawesome/free-solid-svg-icons'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const scenarios = computed(() => store.scenarios)
const error = ref(null)

// watch the params of the route to fetch the data again
watch(() => route.params.id, fetchData, { immediate: true })
watch(
  () => route.name,
  () => {
    if (route.name == 'Scenario Index') {
      store.selected_scenario = null
    }
  },
  { immediate: true }
)

onUpdated(() => {
  //   store.selected_scenario = null
})

onBeforeMount(() => {
  store.selected_scenario = null
})

async function fetchData() {
  error.value = null
  loading.value = true

  try {
    const data = await fetchScenarios()
  } catch (err) {
    error.value = err.toString()
  } finally {
    loading.value = false
  }
}

function selectScenario(uuid) {
  store.selected_scenario = uuid
  router.push({ name: 'Scenario Overview', params: { uuid: uuid }, props: true })
}

function createScenario() {
  router.push({ name: 'New Scenario' })
}

async function deleteScenario(uuid) {
  const result = await doDeleteScenario(uuid)
  ajaxFeedback(result)
  fetchScenarios()
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-center pt-4">
      <FontAwesomeIcon :icon="faSpinner" class="text-4xl fa-spin"></FontAwesomeIcon>
    </div>

    <Alert
      v-if="error"
      variant="danger"
      :title="'Failed to fetch scenarios:'"
      :message="error"
    ></Alert>

    <div v-if="scenarios.length > 0">
      <div class="mb-2 flex flex-row-reverse">
        <button class="btn btn-success" @click="createScenario()">
          <FontAwesomeIcon :icon="faPlus" class="fa-fw"></FontAwesomeIcon>
          Create Scenario
        </button>
      </div>

      <table
        class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full border-separate border border-slate-300 border-spacing-0"
      >
        <thead class="">
          <tr class="font-medium dark:text-slate-200 text-slate-600 bg-slate-150">
            <th class="rounded-tl-lg border-b border-slate-300 p-3 text-left">Namespace</th>
            <th class="border-b border-slate-300 p-3 text-left">Name</th>
            <th class="border-b border-slate-300 p-3 text-left">Description</th>
            <th class="border-b border-slate-300 p-3 text-left">UUID</th>
            <th class="border-b border-slate-300 p-3 text-left">Version</th>
            <!-- <th class="border-b border-slate-300 p-3 text-left">Meta</th> -->
            <th class="border-b border-slate-300 p-3 text-center text-nowrap">
              <FontAwesomeIcon :icon="faHashtag"></FontAwesomeIcon> Injects
            </th>
            <th
              class="rounded-tr-lg border-b border-slate-300 dark:border-slate-700 p-3 text-left"
            ></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="scenario in scenarios"
            :key="scenario.exercise.uuid"
            class="hover:bg-slate-100"
          >
            <td
              class="rounded-bl-lg border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 font-mono text-sm"
            >
              {{ scenario.exercise.namespace }}
            </td>
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 font-semibold cursor-pointer"
              @click="selectScenario(scenario.exercise.uuid)"
            >
              {{ scenario.exercise.name }}
            </td>
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 cursor-pointer"
              @click="selectScenario(scenario.exercise.uuid)"
            >
              {{ scenario.exercise.description }}
            </td>
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 text-xs font-mono select-all"
            >
              {{ scenario.exercise.uuid }}
            </td>
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1"
            >
              {{ scenario.exercise.version }}
            </td>
            <!-- <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1"
            >
              <pre
                class="text-xs bg-gray-200 border border-gray-300 text-black p-1 rounded max-h-17 overflow-auto"
                >{{ scenario.exercise.meta }}</pre
              >
            </td> -->
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 text-center font-semibold"
            >
              {{ scenario.injects.length }}
            </td>
            <td
              class="rounded-br-lg border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 text-left"
            >
              <div class="flex gap-1">
                <button class="btn" @click="selectScenario(scenario.exercise.uuid)">
                  <FontAwesomeIcon :icon="faEdit" class="fa-fw"></FontAwesomeIcon>
                </button>
                <button
                  class="btn btn-danger"
                  @click="
                    toast({
                      title: 'Confirm deletion',
                      message: `You are about to delete scenario ${scenario.exercise.name}. Do you wish to proceed ?`,
                      variant: 'danger',
                      confirm: true,
                      confirmCb: () => {
                        deleteScenario(scenario.exercise.uuid)
                      }
                    })
                  "
                >
                  <FontAwesomeIcon :icon="faTrash" class="fa-fw"></FontAwesomeIcon>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style>
</style>