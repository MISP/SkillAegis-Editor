<script setup>
import { v4 as uuidv4 } from 'uuid'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { Sortable } from 'sortablejs-vue3'
import {
  addNewInjectToSelectedScenario,
  removeInjectFromSelectedScenario,
  updateInjectToSelectedScenario,
  selectedScenario as originalSelectedScenario
} from '@/store.js'
import { Mode } from 'vanilla-jsoneditor'
import {
  faArrowDownWideShort,
  faArrowUpWideShort,
  faCirclePlay,
  faEdit,
  faFingerprint,
  faGripVertical,
  faInfoCircle,
  faListCheck,
  faMinus,
  faPlus,
  faSave,
  faScrewdriverWrench,
  faTimes,
  faTrash
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
import { saveInject, removeInject, saveInjectOrder } from '@/api'
import { ajaxFeedback } from '@/main'

const props = defineProps({
  uuid: String
})

const ALLOWED_STRATEGIES = {
  data_filtering: 'Filter Event data',
  query_mirror: 'Perform the same query against MISP',
  query_search: 'Perform a search query on MISP and compare the returned result'
}
const ALLOWED_TRIGGERS = {
  startex: 'Start of the exercise'
}
const ALLOWED_TARGET_TOOLS = {
  MISP: 'MISP'
}

const route = useRoute()
const router = useRouter()

/* Have to cheat there to avoid having the editor unmount itself before the animation finishes and avoid gutter bug where editor is not displayed correctly */
// onActivated(() => {
//   showEditor.value = true
// })
// onDeactivated(() => {
//   setTimeout(() => {
//     showEditor.value = false
//   }, 250)
//   resetState()
// })

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

onBeforeRouteLeave(async (to, from) => {
  newUnsavedInjects.forEach((inject_uuid) => {
    removeInjectFromSelectedScenario(inject_uuid)
  })
  resetState()
})

const showEditor = ref(true)
const canBeSaved = computed(() => {
  return hasValidChanges.value
})
const hasErrors = computed(() => {
  return getFormErrors.value.length > 0
})

const getFormErrors = computed(() => {
  const errors = []
  if (!selectedInject.value) {
    return errors
  }
  if (
    selectedInject.value.name === undefined ||
    selectedInject.value.name === null ||
    selectedInject.value.name.length < 3
  ) {
    errors.push('selectedInject.name')
  }
  return errors
})

const injectMovedPosition = computed(() => {
  return injectOrderOperations.value.length > 0
})

const hasValidChanges = computed(() => {
  if (!selectedInject.value) {
    return false
  }

  if (hasErrors.value) {
    return false
  }

  const originalSelectedInject = originalSelectedScenario.value.injects.filter(
    (inj) => inj.uuid == selectedInjectFlowUUID.value
  )[0]
  const originalSelectedInjectFlow = originalSelectedScenario.value.inject_flow.filter(
    (inj) => inj.inject_uuid == selectedInjectFlowUUID.value
  )[0]

  const metaChanges =
    originalSelectedInject.name != selectedInject.value.name ||
    (selectedInject.value.description !== '' &&
      originalSelectedInject.description != selectedInject.value.description) ||
    originalSelectedInject.target_tool != selectedInject.value.target_tool

  let sequenceWithoutFakeOptions = {}
  if (typeof selectedInjectFlow.value.sequence === 'object') {
    sequenceWithoutFakeOptions = selectedInjectFlow.value.sequence
    sequenceWithoutFakeOptions.trigger = sequenceWithoutFakeOptions.trigger.filter(
      (item) => item != 'null'
    )
  }
  let sequence_str =
    typeof selectedInjectFlow.value.sequence === 'object'
      ? JSON.stringify(sequenceWithoutFakeOptions, undefined, 4)
      : selectedInjectFlow.value.sequence
  let orig_sequence_str =
    typeof originalSelectedInjectFlow.sequence === 'object'
      ? JSON.stringify(originalSelectedInjectFlow.sequence, undefined, 4)
      : originalSelectedInjectFlow.sequence

  let requirements_str =
    typeof selectedInjectFlow.value.requirements === 'object'
      ? JSON.stringify(selectedInjectFlow.value.requirements, undefined, 4)
      : selectedInjectFlow.value.requirements
  let orig_requirements_str =
    typeof originalSelectedInjectFlow.requirements === 'object'
      ? JSON.stringify(originalSelectedInjectFlow.requirements, undefined, 4)
      : originalSelectedInjectFlow.requirements

  const injectFlowMetaChanges = requirements_str != orig_requirements_str

  if (metaChanges || injectFlowMetaChanges) {
    return true
  }

  for (let i = 0; i < selectedInject.value.inject_evaluation.length; i++) {
    const inject_eval = selectedInject.value.inject_evaluation[i]
    const orig_inject_eval = originalSelectedInject.inject_evaluation[i]

    /* evaluation_context */
    try {
      if (typeof inject_eval.evaluation_context === 'string') {
        JSON.parse(inject_eval.evaluation_context)
      }
      if (typeof inject_eval.parameters === 'string') {
        JSON.parse(inject_eval.parameters)
      }
    } catch (error) {
      return false
    }

    let context_str =
      typeof inject_eval.evaluation_context === 'object'
        ? JSON.stringify(inject_eval.evaluation_context, undefined, 4)
        : inject_eval.evaluation_context
    let orig_context_str =
      typeof orig_inject_eval?.evaluation_context === 'object'
        ? JSON.stringify(orig_inject_eval.evaluation_context, undefined, 4)
        : orig_inject_eval?.evaluation_context

    if (context_str != orig_context_str) {
      return true
    }

    /* evaluation_context */
    try {
      if (typeof inject_eval.evaluation_context === 'string') {
        JSON.parse(inject_eval.evaluation_context)
      }
      if (typeof inject_eval.parameters === 'string') {
        JSON.parse(inject_eval.parameters)
      }
    } catch (error) {
      return false
    }

    let params_str =
      typeof inject_eval.parameters === 'object'
        ? JSON.stringify(inject_eval.parameters, undefined, 4)
        : inject_eval.parameters
    let orig_params_str =
      typeof orig_inject_eval.parameters === 'object'
        ? JSON.stringify(orig_inject_eval.parameters, undefined, 4)
        : orig_inject_eval.parameters

    if (params_str != orig_params_str) {
      return true
    }
  }

  if (
    originalSelectedInject.inject_evaluation.length != selectedInject.value.inject_evaluation.length
  ) {
    return true
  }

  return false
})

const selectedScenario = computed(() => {
  return originalSelectedScenario.value !== null
    ? JSON.parse(JSON.stringify(originalSelectedScenario.value))
    : null
})

let originalInject = {}
let originalInjectFlow = {}
let injectOrderOperations = ref([])
const selectedInject = ref(null)
const selectedInjectFlow = ref(null)
const selectedInjectFlowUUID = ref(null)
let newUnsavedInjects = []

const emptyInject = {
  uuid: '',
  target_tool: 'MISP',
  name: '',
  action: '',
  inject_evaluation: []
}
const emptyInjectFlow = {
  inject_uuid: '',
  description: '',
  requirements: {
    inject_uuid: null
  },
  sequence: {
    followed_by: [],
    trigger: []
  }
}
const emptyInjectEvaluation = {
  parameters: [],
  result: '',
  evaluation_strategy: 'data_filtering',
  evaluation_context: {},
  score_range: [0, 20]
}

const injectByUUID = computed(() => {
  const injects = {}
  if (selectedScenario.value) {
    selectedScenario.value.injects.forEach((inj) => {
      injects[inj.uuid] = inj
    })
  }
  return injects
})

const injectFlowByUUID = computed(() => {
  const injectF = {}
  if (selectedScenario.value) {
    selectedScenario.value.inject_flow.forEach((inj) => {
      injectF[inj.inject_uuid] = inj
    })
  }
  return injectF
})

const inject_flow = computed(() => {
  return selectedScenario.value?.inject_flow || []
})

async function onDragEnd(event) {
  moveInject(event.oldIndex, event.newIndex)
  injectOrderOperations.value.push([event.oldIndex, event.newIndex])
}

async function moveInject(from, to) {
  const item = selectedScenario.value.inject_flow.splice(from, 1)[0]
  await nextTick()
  selectedScenario.value.inject_flow.splice(to, 0, item)
}

function selectInject(uuid) {
  if (selectedInjectFlowUUID.value) {
    revertInjectChanges()
  }
  originalInject = JSON.parse(JSON.stringify(injectByUUID.value[uuid]))
  originalInjectFlow = JSON.parse(JSON.stringify(injectFlowByUUID.value[uuid]))
  selectedInject.value = injectByUUID.value[uuid]
  selectedInjectFlow.value = injectFlowByUUID.value[uuid]
  selectedInjectFlowUUID.value = uuid
}

function resetState() {
  revertInjectChanges()
  revertInjectOrderChanges()
  selectedInject.value = null
  selectedInjectFlow.value = null
  selectedInjectFlowUUID.value = null
}

function revertInjectChanges() {
  if (Object.keys(originalInject).length > 0) {
    injectByUUID.value[selectedInjectFlowUUID.value] = originalInject
    injectFlowByUUID.value[selectedInjectFlowUUID.value] = originalInjectFlow
  }
}

async function saveInjectOrderChanges() {
  const injectOrder = inject_flow.value.map((i) => i.inject_uuid)
  const result = await saveInjectOrder(props.uuid, injectOrder)
  ajaxFeedback(result)
  if (result.success) {
    injectOrderOperations.value = []
  }
}

function cancel() {
  router.push({ name: 'Scenario Overview', params: { uuid: props.uuid }, props: true })
}

function testInject(inject_evaluation) {
  router.push({ name: 'Inject Tester', params: { inject_evaluation: JSON.stringify(inject_evaluation) }, props: true })
}

const sortable = ref()
async function revertInjectOrderChanges() {
  if (sortable.value?.sortable) {
    var order = sortable.value.sortable.toArray()
    injectOrderOperations.value.reverse().forEach(([from, to]) => {
      const item = order.splice(to, 1)[0]
      order.splice(from, 0, item)
    })
    sortable.value.sortable.sort(order, true)
    injectOrderOperations.value = []
  }
}

async function saveInjectChanges() {
  const injectTosave = JSON.parse(JSON.stringify(selectedInject.value))
  injectTosave.inject_evaluation.forEach((i_eval, i) => {
    if (typeof injectTosave.inject_evaluation[i].evaluation_context === 'string') {
      injectTosave.inject_evaluation[i].evaluation_context = JSON.parse(i_eval.evaluation_context)
    }
    if (typeof injectTosave.inject_evaluation[i].parameters === 'string') {
      injectTosave.inject_evaluation[i].parameters = JSON.parse(i_eval.parameters)
    }
  })

  const injectFlowToSave = JSON.parse(JSON.stringify(selectedInjectFlow.value))

  const result = await saveInject(props.uuid, injectTosave, injectFlowToSave)
  if (result.success) {
    newUnsavedInjects = newUnsavedInjects.filter((e) => e !== injectTosave.uuid)
    updateInjectToSelectedScenario(injectTosave, injectFlowToSave)
    originalInject = JSON.parse(JSON.stringify(injectTosave))
    originalInjectFlow = JSON.parse(JSON.stringify(injectFlowToSave))
  }
  ajaxFeedback(result)
}

function createNewInject() {
  const uuid = uuidv4()
  const newInject = JSON.parse(JSON.stringify(emptyInject))
  newInject.uuid = uuid
  const newInjectFlow = JSON.parse(JSON.stringify(emptyInjectFlow))
  newInjectFlow.inject_uuid = uuid
  newUnsavedInjects.push(uuid)
  addNewInjectToSelectedScenario(newInject, newInjectFlow)
  selectInject(uuid)
}

async function deleteInject(inject_uuid) {
  let result = { success: true }
  let ajaxDone = false
  if (!newUnsavedInjects.includes(inject_uuid)) {
    result = await removeInject(props.uuid, inject_uuid)
    ajaxDone = true
  }
  if (result.success) {
    newUnsavedInjects = newUnsavedInjects.filter((e) => e !== inject_uuid)
    removeInjectFromSelectedScenario(inject_uuid)
    if (selectedInjectFlowUUID.value == inject_uuid) {
      resetState()
    }
  }
  return ajaxDone ? ajaxFeedback(result) : true
}

function createNewInjectEval() {
  const newInjectEvaluation = JSON.parse(JSON.stringify(emptyInjectEvaluation))
  selectedInject.value.inject_evaluation.push(newInjectEvaluation)
}

function deleteEvaluation(evaluationIndex) {
  selectedInject.value.inject_evaluation.splice(evaluationIndex, 1)
}
</script>

<template>
  <div>
    <div class="flex justify-end gap-2">
      <button class="btn btn-danger select-none" @click="cancel()">
        <FontAwesomeIcon :icon="faTimes" class="fa-fw"></FontAwesomeIcon> Cancel Changes
      </button>
      <button
        :class="`btn btn-success select-none ${canBeSaved ? 'highlight-success' : ''}`"
        @click="saveInjectChanges()"
        :disabled="!canBeSaved"
      >
        <FontAwesomeIcon :icon="faEdit" class="fa-fw"></FontAwesomeIcon> Save Inject Changes
      </button>
    </div>

    <div class="flex flex-row gap-8">
      <div class="basis-2/5">
        <div class="flex gap-2">
          <h2 class="text-2xl">Injects</h2>
          <div class="ml-auto flex gap-2">
            <button
              class="btn btn-danger select-none"
              :disabled="!injectMovedPosition"
              @click="revertInjectOrderChanges()"
            >
              <FontAwesomeIcon :icon="faArrowUpWideShort" class="fa-fw"></FontAwesomeIcon>Reset Order
            </button>
            <button
              :class="`btn btn-success select-none ${
                injectMovedPosition ? 'highlight-success' : ''
              }`"
              @click="saveInjectOrderChanges()"
              :disabled="!injectMovedPosition"
            >
              <FontAwesomeIcon :icon="faArrowDownWideShort" class="fa-fw"></FontAwesomeIcon>Save
              Inject Order
            </button>
          </div>
        </div>
        <div class="pl-2 flex flex-col gap-1 py-2">
          <Alert
            v-if="inject_flow.length == 0"
            variant="warning"
            title="No inject available"
            message="Create an inject to get started."
          ></Alert>
          <Sortable
            ref="sortable"
            :list="inject_flow"
            item-key="inject_uuid"
            tag="div"
            :options="{
              animation: 170,
              ghostClass: 'ghost',
              dragClass: 'drag',
              handle: '.drag-handle',
              // filter: '.unsaved-inject',
              forceFallback: true
            }"
            @end="onDragEnd"
            class="flex flex-col gap-1"
          >
            <template #item="{ element }">
              <div
                @click="selectInject(element.inject_uuid)"
                :class="`
                    group flex flex-col gap-1 py-1 px-2 rounded select-none cursor-pointer border
                    ${
                      selectedInjectFlowUUID == element.inject_uuid
                        ? 'border-blue-400 bg-blue-100 -translate-x-2'
                        : 'border-slate-400 bg-slate-50'
                    }
                  `"
              >
                <div class="flex flex-row gap-2 items-center">
                  <FontAwesomeIcon
                    :icon="faGripVertical"
                    class="fa-fw drag-handle absolute text-lg cursor-grab"
                  ></FontAwesomeIcon>
                  <span class="font-semibold ml-7">
                    {{ injectByUUID[element.inject_uuid].name }}
                  </span>
                  <FontAwesomeIcon :icon="faMinus" class="fa-fw"></FontAwesomeIcon>
                  <span class="font-light">
                    <span v-if="injectByUUID[element.inject_uuid].description">{{
                      injectByUUID[element.inject_uuid].description
                    }}</span>
                    <span v-else class="font-light text-sm text-gray-500">- No description -</span>
                  </span>
                  <span class="ml-auto">
                    <button
                      class="hidden group-hover:inline-block btn btn-xs btn-danger select-none !border-slate-400"
                      @click.stop="deleteInject(element.inject_uuid)"
                    >
                      <FontAwesomeIcon :icon="faTrash" class="fa-fw"></FontAwesomeIcon>
                    </button>
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
                        element.inject_uuid
                      }}</span>
                    </div>
                  </span>

                  <span class="bg-slate-300 rounded py-0.5 px-1 inline-flex flex-col font-semibold">
                    <div class="justify-start text-nowrap">
                      <FontAwesomeIcon :icon="faCirclePlay" class="fa-fw"></FontAwesomeIcon>
                      Trigger
                    </div>
                    <span class="bg-slate-50 p-0.5 mt-0.5 rounded">
                      <span
                        v-if="
                          injectFlowByUUID[element.inject_uuid].sequence.trigger.filter(
                            (t) => t != '- No trigger -'
                          ).length > 0
                        "
                        >{{
                          injectFlowByUUID[element.inject_uuid].sequence.trigger
                            .filter((t) => t != '- No trigger -')
                            .join(', ')
                        }}</span
                      >
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
                      {{ injectByUUID[element.inject_uuid].target_tool }}
                    </span>
                  </span>

                  <span class="bg-slate-300 rounded py-0.5 px-1 inline-flex flex-col font-semibold">
                    <div class="justify-start text-nowrap">
                      <FontAwesomeIcon :icon="faListCheck" class="fa-fw"></FontAwesomeIcon>
                      Inject Evaluation
                    </div>
                    <span class="bg-slate-50 p-0.5 mt-0.5 rounded">
                      {{ injectByUUID[element.inject_uuid].inject_evaluation.length }}
                    </span>
                  </span>
                </div>
              </div>
            </template>
          </Sortable>
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
            <div class="flex flex-col gap-3">
              <div class="flex flex-row gap-6">
                <div class="basis-1/4">
                  <label for="name" class="block text-gray-700 font-bold mb-1">Inject Name</label>
                  <input
                    type="text"
                    v-model="selectedInject.name"
                    :class="`shadow border w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border-slate-400 ${
                      getFormErrors.includes('selectedInject.name') ? 'form-error' : ''
                    }`"
                    id="name"
                    placeholder="A name"
                  />
                </div>

                <div class="flex-grow">
                  <label for="description" class="block text-gray-700 font-bold mb-1"
                    >Inject Description</label
                  >
                  <input
                    type="text"
                    v-model="selectedInject.description"
                    :class="`shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400 ${
                      getFormErrors.includes('selectedInject.description') ? 'form-error' : ''
                    }`"
                    id="description"
                    placeholder="A description"
                  />
                </div>
                <div class="">
                  <label for="target_tool" class="block text-gray-700 font-bold mb-1">
                    <FontAwesomeIcon :icon="faScrewdriverWrench" class="fa-fw"></FontAwesomeIcon>
                    Target Tool
                  </label>
                  <select
                    v-model="selectedInject.target_tool"
                    class="shadow border w-full rounded py-2 px-2 text-gray-700 leading-tight focus:outline-none focus:border-slate-400 bg-white"
                    id="target_tool"
                    placeholder="MISP"
                  >
                    <option
                      v-for="(tool_info, tool) in ALLOWED_TARGET_TOOLS"
                      :key="tool"
                      :value="tool"
                      :title="tool_info"
                    >
                      {{ tool }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="flex flex-row gap-6">
                <div class="basis-1/3">
                  <label for="name" class="block text-gray-700 font-bold mb-1">Triggers</label>
                  <Dropdown
                    v-model="selectedInjectFlow.sequence.trigger"
                    :options="ALLOWED_TRIGGERS"
                    searchable
                    multiple
                    placeholder="- No trigger -"
                  >
                  <template #tag_text="{option, textGetter}">
                    <span class="text-red-700 font-mono py-0.5 px-1 rounded-sm bg-gray-50 mr-1">[{{ option }}]</span> {{ textGetter(option) }}
                  </template>
                  <template #option="{option, textGetter}">
                    <span class="text-red-700 font-mono py-0.5 px-1 rounded-sm bg-gray-50 border mr-1">[{{ option }}]</span> {{ textGetter(option) }}
                  </template>
                  </Dropdown>
                </div>
                <div class="basis-2/3">
                  <label for="requirement" class="block text-gray-700 font-bold mb-1"
                    >Inject Completion Requirement</label
                  >
                  <Dropdown
                    id="requirement"
                    v-model="selectedInjectFlow.requirements.inject_uuid"
                    :options="Object.values(injectByUUID).map((inject) => {
                      return {
                        value: inject.uuid,
                        label: inject.name,
                        disabled: inject.uuid == selectedInject.uuid
                      }
                    })"
                    trackBy="value"
                    searchable
                    placeholder="- No requirements -"
                  ></Dropdown>
                </div>
              </div>
            </div>
          </form>

          <div>
            <h2 class="text-xl mb-2">Inject Evaluations</h2>
            <div>
              <Alert
                v-if="selectedInject?.inject_evaluation.length == 0"
                variant="info"
                title="No evaluation available"
                message="Add an inject to get started."
              ></Alert>
              <div
                v-for="(inject_eval, i) in selectedInject?.inject_evaluation"
                :key="i"
                class="flex flex-col gap-1 py-1 px-2 border border-slate-400 rounded bg-slate-200 mb-5"
              >
                <div class="relative">
                  <span
                    class="font-semibold select-none absolute px-1 -top-1 -left-2 bg-slate-300 border-slate-400 text-slate-700 rounded-br rounded-tl border-b border-r"
                  >
                    <span>Evaluation {{ i + 1 }}</span>
                    <button
                      class="btn btn-sm btn-danger select-none ml-2"
                      @click="deleteEvaluation(i)"
                    >
                      <FontAwesomeIcon :icon="faTrash" class="fa-fw"></FontAwesomeIcon>
                    </button>
                    <button
                      class="btn btn-sm btn-info select-none"
                      @click="testInject(selectedInject.inject_evaluation[i])"
                    >
                      <FontAwesomeIcon :icon="faListCheck" class="fa-fw"></FontAwesomeIcon>
                    </button>
                  </span>
                  <div class="flex gap-3 mt-8">
                    <div class="basis-1/3">
                      <div>
                        <div class="font-semibold pt-1 text-nowrap">Evaluation Strategy</div>
                        <div class="min-w-60">
                          <select
                            v-model="selectedInject.inject_evaluation[i].evaluation_strategy"
                            class="shadow border w-full rounded py-2 px-2 text-gray-700 leading-tight focus:outline-none focus:border-slate-400 bg-white"
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

              <div class="flex justify-center">
                <button class="btn btn-success select-none" @click="createNewInjectEval()">
                  <FontAwesomeIcon :icon="faPlus" class="fa-fw"></FontAwesomeIcon>Add New Evaluation
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
button.highlight-success {
  @apply bg-green-400;
}
input.form-error {
  @apply border-2 border-red-400;
}

label {
  @apply select-none;
}

.ghost {
  @apply bg-slate-300;
  @apply border-dashed;
  @apply -translate-x-4;
}

.drag {
  @apply !opacity-60;
}
</style>
