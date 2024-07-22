<script setup>
import { v4 as uuidv4 } from 'uuid'
import { useRoute, useRouter } from 'vue-router'
import { addNewInjectToSelectedScenario, selectedScenario } from '@/store.js'
import { Mode } from 'vanilla-jsoneditor'
import {
  faCirclePlay,
  faEdit,
  faFingerprint,
  faInfoCircle,
  faListCheck,
  faMinus,
  faPlus,
  faSave,
  faScrewdriverWrench,
  faTimes
} from '@fortawesome/free-solid-svg-icons'
import {
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
  watch,
  onActivated,
  onDeactivated,
  nextTick
} from 'vue'
import JsonEditorVue from 'json-editor-vue'

const props = defineProps({
  uuid: String
})

const ALLOWED_STRATEGIES = {
  data_filtering: 'Filter Event data',
  query_mirror: 'Perform the same query against MISP',
  query_search: 'Perform a search query on MISP and compare the returned result'
}

const route = useRoute()
const router = useRouter()

/* Have to cheat there to avoid having the editor unmount itself before the animation finishes and avoid gutter bug where editor is not displayed correctly */
onActivated(() => {
  showEditor.value = true
})
onDeactivated(() => {
  setTimeout(() => {
    showEditor.value = false
  }, 250)
})

onBeforeUnmount(() => {
  resetState()
})

onMounted(() => {
  resetState()
})

watch(
  () => route.params.uuid,
  () => {
    resetState()
  }
)

const showEditor = ref(false)
const canBeSaved = computed(() => {
  return false
})

const selectedInject = ref(null)
const selectedInjectFlowUUID = ref(null)
const selectedInjectFlow = ref(null)

const emptyInject = {
  uuid: '',
  target_tool: 'MISP',
  name: '',
  action: '',
  inject_evaluation: [
    {
      evaluation_strategy: 'data_filtering',
      result: '',
      score_range: [0, 20],
      evaluation_context: {},
      parameters: []
    }
  ]
}
const emptyInjectFlow = {
  inject_uuid: '',
  requirements: {},
  sequence: {
    followed_by: [],
    trigger: []
  }
}

const unsavedNewInjectUUIDs = []

const injectByUUID = computed(() => {
  const injects = {}
  selectedScenario.value.injects.forEach((inj) => {
    injects[inj.uuid] = inj
  })
  return injects
})

const injectFlowByUUID = computed(() => {
  const injectF = {}
  inject_flows.value.forEach((inj) => {
    injectF[inj.inject_uuid] = inj
  })
  return injectF
})

const inject_flows = computed(() => {
  return selectedScenario.value?.inject_flow || []
})

function selectInject(uuid) {
  selectedInject.value = injectByUUID.value[uuid]
  selectedInjectFlow.value = injectFlowByUUID.value[uuid]
  selectedInjectFlowUUID.value = uuid
  // resetForm()
  // updateForm()
}

// function updateForm() {
//   inject_name.value = selectedInject.value.name
//   inject_description.value = selectedInject.value.description
//   inject_target_tool.value = selectedInject.value.target_tool

//   selectedInject.value?.inject_evaluation.forEach((inject_eval) => {
//     inject_eval_strategy.value.push(inject_eval.evaluation_strategy)
//     inject_eval_score.value.push(inject_eval.score_range[1])
//     inject_eval_result.value.push(inject_eval.result)
//     inject_eval_context.value.push(JSON.stringify(inject_eval.evaluation_context, null, 4))
//     inject_eval_params.value.push(JSON.stringify(inject_eval.parameters, null, 4))
//   })
// }

function resetState() {
  selectedInject.value = null
  // resetForm()
}

// function resetForm() {
//   inject_name.value = ''
//   inject_description.value = ''
//   inject_target_tool.value = 'MISP'

//   inject_eval_strategy.value = []
//   inject_eval_score.value = []
//   inject_eval_result.value = []
//   inject_eval_context.value = []
//   inject_eval_params.value = []
// }

// const inject_name = ref('')
// const inject_description = ref('')
// const inject_target_tool = ref('MISP')

// const inject_eval_strategy = ref([])
// const inject_eval_score = ref([])
// const inject_eval_result = ref([])
// const inject_eval_context = ref([])
// const inject_eval_params = ref([])

function cancel() {
  router.push({ name: 'Scenario Overview', params: { uuid: props.uuid }, props: true })
}

async function saveScenario() {}

function createNewInject() {
  const uuid = uuidv4()
  const newInject = Object.assign({}, emptyInject)
  newInject.uuid = uuid
  unsavedNewInjectUUIDs.push(uuid)
  const newInjectFlow = Object.assign({}, emptyInjectFlow)
  newInjectFlow.inject_uuid = uuid
  addNewInjectToSelectedScenario(newInject, newInjectFlow)
  selectInject(uuid)
}

function createNewInjectEval() {}
</script>

<template>
  <div>
    <div class="flex justify-end my-2 gap-2">
      <button class="btn btn-danger select-none" @click="cancel()">
        <FontAwesomeIcon :icon="faTimes" class="fa-fw"></FontAwesomeIcon>Cancel Changes
      </button>
      <button class="btn btn-success select-none" @click="saveScenario()" :disabled="!canBeSaved">
        <FontAwesomeIcon :icon="faEdit" class="fa-fw"></FontAwesomeIcon>Save Scenario
      </button>
    </div>

    <div class="flex flex-row gap-8">
      <div class="basis-2/5">
        <h2 class="text-2xl">Injects</h2>
        <div class="pl-2 flex flex-col gap-1 py-2">
          <Alert
            v-if="inject_flows.length == 0"
            variant="warning"
            title="No inject available"
            message="Create an inject to get started."
          ></Alert>
          <div
            v-for="injectF in inject_flows"
            :key="injectF.inject_uuid"
            :class="`
              flex flex-col gap-1 py-1 px-2 rounded select-none cursor-pointer
              hover:-translate-x-3 transition-all duration-75 border
              ${
                selectedInjectFlowUUID == injectF.inject_uuid
                  ? 'border-blue-400 bg-blue-200 -translate-x-2'
                  : 'border-slate-400 bg-slate--200'
              }
            `"
            @click="selectInject(injectF.inject_uuid)"
          >
            <div class="flex flex-row gap-2 items-center">
              <span class="font-semibold">
                {{ injectByUUID[injectF.inject_uuid].name }}
              </span>
              <FontAwesomeIcon :icon="faMinus" class="fa-fw"></FontAwesomeIcon>
              <span class="font-light">
                <span v-if="injectByUUID[injectF.inject_uuid].description">{{
                  injectByUUID[injectF.inject_uuid].description
                }}</span>
                <span v-else class="font-light text-sm text-gray-500">- No description -</span>
              </span>
            </div>

            <div class="flex flex-row gap-3 text-xs">
              <span class="bg-slate-300 rounded py-0.5 px-1 inline-flex flex-col font-semibold">
                <div class="justify-start text-nowrap">
                  <FontAwesomeIcon :icon="faFingerprint" class="fa-fw"></FontAwesomeIcon>
                  UUID
                </div>
                <div class="bg-slate-50 p-0.5 rounded">
                  <span class="text-nowrap font-mono font-light text-2xs text-gray-800">{{
                    injectF.inject_uuid
                  }}</span>
                </div>
              </span>

              <span class="bg-slate-300 rounded py-0.5 px-1 inline-flex flex-col font-semibold">
                <div class="justify-start text-nowrap">
                  <FontAwesomeIcon :icon="faCirclePlay" class="fa-fw"></FontAwesomeIcon>
                  Trigger
                </div>
                <span class="bg-slate-50 p-0.5 mt-0.5 rounded">
                  <span v-if="injectF.sequence.trigger.length > 0">{{
                    injectF.sequence.trigger.join(', ')
                  }}</span>
                  <span v-else class="text-nowrap font-light text-xs text-gray-500"
                    >- No trigger -</span
                  >
                </span>
              </span>

              <span class="bg-slate-300 rounded py-0.5 px-1 inline-flex flex-col font-semibold">
                <div class="justify-start text-nowrap">
                  <FontAwesomeIcon :icon="faScrewdriverWrench" class="fa-fw"></FontAwesomeIcon>
                  Target Tool
                </div>
                <span class="bg-slate-50 p-0.5 mt-0.5 rounded">
                  {{ injectByUUID[injectF.inject_uuid].target_tool }}
                </span>
              </span>

              <span class="bg-slate-300 rounded py-0.5 px-1 inline-flex flex-col font-semibold">
                <div class="justify-start text-nowrap">
                  <FontAwesomeIcon :icon="faListCheck" class="fa-fw"></FontAwesomeIcon>
                  Inject Evaluation
                </div>
                <span class="bg-slate-50 p-0.5 mt-0.5 rounded">
                  {{ injectByUUID[injectF.inject_uuid].inject_evaluation.length }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <div class="flex justify-end">
          <button class="btn btn-success select-none" @click="createNewInject()">
            <FontAwesomeIcon :icon="faPlus" class="fa-fw"></FontAwesomeIcon>Create New Inject
          </button>
        </div>
      </div>

      <div class="basis-3/5">
        <h2 class="text-2xl mb-2">Design Inject</h2>
        <Alert v-show="!selectedInject" variant="info" :title="'Select an inject to edit'"></Alert>
        <div v-if="selectedInject">
          <form class="mb-3">
            <div class="flex flex-col gap-6">
              <div class="flex flex-row gap-6">
                <div class="basis-1/4">
                  <label for="name" class="block text-gray-700 font-bold mb-2">Inject Name</label>
                  <input
                    type="text"
                    v-model="selectedInject.name"
                    class="shadow border w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border-slate-400"
                    id="name"
                    placeholder="A name"
                  />
                </div>

                <div class="flex-grow">
                  <label for="description" class="block text-gray-700 font-bold mb-2"
                    >Inject Description</label
                  >
                  <input
                    type="text"
                    v-model="selectedInject.description"
                    class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                    id="description"
                    placeholder="A description"
                  />
                </div>
                <div class="">
                  <label for="target_tool" class="block text-gray-700 font-bold mb-2">
                    <FontAwesomeIcon :icon="faScrewdriverWrench" class="fa-fw"></FontAwesomeIcon>
                    Target Tool
                  </label>
                  <select
                    v-model="selectedInject.target_tool"
                    class="shadow border w-full rounded py-2 px-2 text-gray-700 leading-tight focus:outline-none focus:border-slate-400"
                    id="target_tool"
                    placeholder="MISP"
                  >
                    <option value="MISP">MISP</option>
                  </select>
                </div>
              </div>
            </div>
          </form>

          <div>
            <h2 class="text-xl mb-2">Inject Evaluation</h2>
            <div>
              <div
                v-for="(inject_eval, i) in selectedInject?.inject_evaluation"
                :key="i"
                class="flex flex-col gap-1 py-1 px-2 border border-slate-400 rounded bg-slate-200 mb-5"
              >
                <div class="relative">
                  <span
                    class="font-semibold absolute px-1 -top-1 -left-2 bg-slate-300 border-slate-400 text-slate-700 rounded-br rounded-tl border-b border-r"
                  >
                    Inject {{ i + 1 }}
                  </span>
                  <div class="flex gap-3 mt-5">
                    <div class="basis-1/3">
                      <div>
                        <div class="font-semibold pt-1 text-nowrap">Evaluation Strategy</div>
                        <div class="min-w-60">
                          <select
                            v-model="selectedInject.inject_evaluation[i].evaluation_strategy"
                            class="shadow border w-full rounded py-2 px-2 text-gray-700 leading-tight focus:outline-none focus:border-slate-400"
                            placeholder="Evaluation Strategy"
                          >
                            <option
                              v-for="(strategy_info, strategy) in ALLOWED_STRATEGIES"
                              :key="strategy"
                              :value="strategy"
                              :title="strategy_info"
                            >
                              {{ strategy }}
                            </option>
                          </select>
                        </div>
                      </div>
                      <div>
                        <div class="font-semibold pt-2">Max Score</div>
                        <div class="min-w-60">
                          <input
                            type="number"
                            min="0"
                            v-model="selectedInject.inject_evaluation[i].score_range[1]"
                            class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                            placeholder="20"
                          />
                        </div>
                      </div>
                      <div>
                        <div class="font-semibold pt-2">Result</div>
                        <div class="min-w-60">
                          <input
                            type="text"
                            v-model="selectedInject.inject_evaluation[i].result"
                            class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                            placeholder="Data created"
                          />
                        </div>
                      </div>
                    </div>
                    <div class="basis-2/3 -mt-5">
                      <div class="font-semibold">Evaluation Context</div>
                      <div class="min-w-60">
                        <JsonEditorVue
                          v-if="showEditor"
                          v-model="selectedInject.inject_evaluation[i].evaluation_context"
                          :mode="Mode.text"
                          :mainMenuBar="false"
                          :navigationBar="false"
                          :statusBar="false"
                          :indentation="2"
                          class="shadow-lg border w-full"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 class="text-lg my-2">Evaluation Parameters</h3>
                  <JsonEditorVue
                    v-if="showEditor"
                    v-model="selectedInject.inject_evaluation[i].parameters"
                    :mode="Mode.text"
                    :mainMenuBar="false"
                    :indentation="4"
                    class="shadow-lg border w-full"
                  />
                </div>
              </div>

              <div class="flex justify-end">
                <button class="btn btn-success select-none" @click="createNewInjectEval()">
                  <FontAwesomeIcon :icon="faPlus" class="fa-fw"></FontAwesomeIcon>Create New
                  Evaluation
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>