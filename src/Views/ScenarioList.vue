<script setup>
import { store } from '@/store.js'
import { ref, watch, onUpdated, onBeforeMount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ajaxFeedback, toast } from '@/main.js'
import {
  deleteScenario as doDeleteScenario,
  fetchScenarios,
  forceReload,
  saveJSON as saveJSONAPI
} from '@/api.js'
import {
  faWarning,
  faHashtag,
  faSpinner,
  faEdit,
  faTrash,
  faPlus,
  faArrowsRotate,
  faEye,
  faFileCode,
  faCircleCheck,
  faCircleXmark
} from '@fortawesome/free-solid-svg-icons'
import JsonEditorVue from 'json-editor-vue'
import { Mode, createAjvValidator } from 'vanilla-jsoneditor'

const route = useRoute()
const router = useRouter()

const validator = ref()

const loading = ref(false)
const scenarios = computed(() => store.scenarios)
const read_errors = computed(() => store.read_errors)
const scenario_validated_by_uuid = computed(() => store.scenario_validated_by_uuid)
const scenario_filename_by_uuid = computed(() => store.scenario_filename_by_uuid)
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
    await fetchScenarios()
    const schema = JSON.parse(
      // AjvValidator doesn't support `uuid` format by default. Cheap trick to make it works without hurdles
      JSON.stringify(store.cexf_schema).replaceAll(
        '"format":"uuid"',
        '"pattern":"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"'
      )
    )
    const schemaDefinitions = {}
    validator.value = createAjvValidator({ schema, schemaDefinitions })
  } catch (err) {
    error.value = err.toString()
  } finally {
    loading.value = false
  }
}

async function reload() {
  error.value = null
  loading.value = true

  try {
    await forceReload()
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

async function saveJSON() {
  const result = await saveJSONAPI(selectedFilename.value, selectedFileContent.value)
  ajaxFeedback(result)
  fetchScenarios()
  return result.success
}

const showModal = ref(false)
const showModalError = ref(false)
const selectedFilename = ref('')
const selectedFileError = ref('')
const selectedFileContent = ref('')
const selectedParsedFileContent = ref('')
function viewFileError(filename, read_error) {
  showModalError.value = true
  selectedFilename.value = filename
  selectedFileError.value = read_error.error
  selectedFileContent.value = read_error.text
}
function viewFile(filename, content, parsedContent) {
  showModal.value = true
  selectedFilename.value = filename
  selectedFileContent.value = content
  selectedParsedFileContent.value = parsedContent
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-center pt-4">
      <FontAwesomeIcon :icon="faSpinner" class="text-4xl fa-spin"></FontAwesomeIcon>
    </div>

    <Modal :showModal="showModalError" @modal-close="showModalError = false">
      <template #header>
        Content of file<code class="font-semibold ml-2">{{ selectedFilename }}</code>
      </template>
      <template #body>
        <div>
          <strong>Error:</strong>
          <span class="ml-2 font-mono">{{ selectedFileError }}</span>
        </div>
        <div
          class="mt-2 border border-slate-900 bg-white p-2 overflow-auto max-h-[calc(100vh-24rem)]"
        >
          <JsonEditorVue
            v-model="selectedFileContent"
            :mode="Mode.text"
            :mainMenuBar="false"
            :navigationBar="false"
            :statusBar="false"
            :indentation="2"
            :validator="validator"
            class="shadow-lg border w-full max-h-[calc(100vh-24rem-2rem)] overflow-y-auto"
          />
        </div>
      </template>
      <template #footer="{ close }">
        <div class="flex flex-row-reverse gap-2">
          <button class="btn btn-primary btn-lg" @click.stop="close()">Ok</button>
          <button class="btn btn-success btn-lg" @click.stop="saveJSON() && close()">
            Save JSON
          </button>
        </div>
      </template>
    </Modal>
    <Modal :showModal="showModal" @modal-close="showModal = false">
      <template #header
        >Content of scenario
        <code class="font-semibold ml-2">{{ selectedFilename }}</code></template
      >
      <template #body>
        <div>
          <div class="p-1"></div>
          <div
            v-show="scenario_validated_by_uuid[selectedParsedFileContent.exercise.uuid] !== true"
          >
            <div class="font-bold text-slate-800">CEXF Schema validation error:</div>
            <pre
              class="max-h-32 p-1 text-sm bg-white border border-red-600 shadow rounded overflow-auto mb-2"
              >{{ scenario_validated_by_uuid[selectedParsedFileContent.exercise.uuid] }}</pre
            >
          </div>
          <JsonEditorVue
            v-model="selectedFileContent"
            :mode="Mode.text"
            :mainMenuBar="false"
            :navigationBar="false"
            :statusBar="false"
            :indentation="2"
            :validator="validator"
            class="shadow-lg border w-full max-h-[calc(100vh-24rem-2rem)] overflow-y-auto"
          />
        </div>
      </template>
      <template #footer="{ close }">
        <div class="flex flex-row-reverse gap-2">
          <button class="btn btn-primary btn-lg" @click.stop="close()">Ok</button>
          <button class="btn btn-success btn-lg" @click.stop="saveJSON() && close()">
            Save JSON
          </button>
        </div>
      </template>
    </Modal>

    <Alert
      v-if="error"
      variant="danger"
      :title="'Failed to fetch scenarios:'"
      :message="error"
    ></Alert>

    <div v-if="scenarios.length > 0">
      <div class="flex">
        <h2 class="text-lg text-slate-700 mb-1">Available Scenarios</h2>
        <div class="ml-auto mb-2 inline-flex flex-row-reverse gap-2">
          <button class="btn btn-success" @click="createScenario()">
            <FontAwesomeIcon :icon="faPlus" class="fa-fw"></FontAwesomeIcon>
            Create Scenario
          </button>
          <button class="btn" @click="reload()">
            <FontAwesomeIcon :icon="faArrowsRotate" class="fa-fw"></FontAwesomeIcon>
            Reload Scenarios
          </button>
        </div>
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
              class="rounded-bl-lg border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 px-2 py-1 font-mono text-sm"
            >
              {{ scenario.exercise.namespace }}
            </td>
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 font-semibold cursor-pointer"
              @click="selectScenario(scenario.exercise.uuid)"
            >
              <span
                :title="
                  scenario_validated_by_uuid[scenario.exercise.uuid] === true
                    ? 'CEXF Schema validity: Valid'
                    : 'CEXF Schema validity: Invalid \n' +
                      scenario_validated_by_uuid[scenario.exercise.uuid]
                "
              >
                <FontAwesomeIcon
                  :icon="
                    scenario_validated_by_uuid[scenario.exercise.uuid] === true
                      ? faCircleCheck
                      : faCircleXmark
                  "
                  :class="
                    scenario_validated_by_uuid[scenario.exercise.uuid] === true
                      ? 'text-green-600'
                      : 'text-red-600'
                  "
                ></FontAwesomeIcon>
              </span>
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
            <td
              class="border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 text-center font-semibold"
            >
              {{ scenario.injects.length }}
            </td>
            <td
              class="rounded-br-lg border-b border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-400 p-1 text-left"
            >
              <div class="flex gap-1">
                <button
                  class="btn"
                  @click="
                    viewFile(
                      scenario_filename_by_uuid[scenario.exercise.uuid],
                      JSON.stringify(scenario, undefined, 2),
                      scenario
                    )
                  "
                >
                  <FontAwesomeIcon :icon="faFileCode" class="fa-fw"></FontAwesomeIcon>
                </button>
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

    <div class="mt-5 mb-1" v-if="Object.keys(read_errors).length > 0">
      <h2 class="text-lg text-slate-700 mb-1">Read Errors</h2>
      <div
        class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full border-separate [&:not(:last-child)]border border-slate-300 border-spacing-0"
      >
        <div
          v-for="(read_error, filename) in read_errors"
          :key="filename"
          class="px-3 py-2 flex border-b border-slate-100"
        >
          <span class="font-mono font-semibold flex items-center">{{ filename }}</span>
          <span class="font-mono text-sm flex items-center ml-5">{{ read_error.error }}</span>
          <span class="ml-auto">
            <div class="flex gap-1">
              <button class="btn" @click="viewFileError(filename, read_error)">
                <FontAwesomeIcon :icon="faEye" class="fa-fw"></FontAwesomeIcon>
              </button>
            </div>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.jse-main .jse-contents {
  overflow: auto;
  max-height: calc(100vh - 24rem - 13rem);
}
</style>