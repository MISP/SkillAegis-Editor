<script setup>
import { useRouter } from 'vue-router'
import { selectedScenario, selectedScenarioUUID } from '@/store.js'
import { faHashtag, faPenRuler, faSave, faTimes } from '@fortawesome/free-solid-svg-icons'
import { ref, computed, onMounted, onBeforeUnmount, watch, onActivated, onDeactivated } from 'vue'
import JsonEditorVue from 'json-editor-vue'
import { Mode } from 'vanilla-jsoneditor'
import { editScenario, fetchScenarios } from '@/api'
import { ajaxFeedback } from '@/main'

const props = defineProps({
  uuid: String
})

const router = useRouter()
const editor = ref()
const theEditor = computed(() => editor.value?.jsonEditor)
const showEditor = ref(false)
const canBeSaved = computed(() => {
  return hasValidChanges.value
})
const parsedMeta = computed(() => {
  try {
    return JSON.parse(exercise_meta.value)
  } catch (error) {
    return false
  }
})
const hasValidChanges = computed(() => {
  if (selectedScenario.value?.exercise && parsedMeta.value !== false) {
    return (
      selectedScenario.value.exercise.name != exercise_name.value ||
      selectedScenario.value.exercise.namespace != exercise_namespace.value ||
      selectedScenario.value.exercise.uuid != exercise_uuid.value ||
      selectedScenario.value.exercise.version != exercise_version.value ||
      JSON.stringify(selectedScenario.value.exercise.meta) != JSON.stringify(parsedMeta.value)
    )
  }
  return false
})

/* Have to cheat there to avoid having the editor unmount itself before the animation finishes and avoid gutter bug where editor is not displayed correctly */
onActivated(() => {
  showEditor.value = true
})
onDeactivated(() => {
  setTimeout(() => {
    showEditor.value = false
  }, 250)
})

const exercise_name = ref('')
const exercise_namespace = ref('')
const exercise_uuid = ref('')
const exercise_version = ref('')
const exercise_meta = ref('{}')

const injectCount = computed(() => {
  return selectedScenario.value?.inject_flow.length || 0
})
const injectPayloadCount = computed(() => {
  return selectedScenario.value?.inject_payloads.length || 0
})

const injectTargetToolUsed = computed(() => {
  const tools = new Set()
  selectedScenario.value?.injects.forEach((inject) => {
    tools.add(inject.target_tool)
  })
  return Array.from(tools)
})

async function saveScenario() {
  const result = await editScenario({
    name: exercise_name.value,
    namespace: exercise_namespace.value,
    uuid: exercise_uuid.value,
    version: exercise_version.value,
    meta: parsedMeta.value
  })
  ajaxFeedback(result)
  fetchScenarios()
}

function cancel() {
  router.push({ name: 'Scenario Index' })
}

function designScenario() {
  router.push({ name: 'Scenario Designer', params: { uuid: props.uuid }, props: true })
}

onMounted(() => {
  initForm()
})

watch(selectedScenario, () => {
  initForm()
})

onBeforeUnmount(() => {
  resetForm()
})

function resetForm() {
  exercise_name.value = ''
  exercise_namespace.value = ''
  exercise_uuid.value = ''
  exercise_version.value = ''
  exercise_meta.value = {}
}

function initForm() {
  if (selectedScenario.value?.exercise) {
    exercise_name.value = selectedScenario.value.exercise.name
    exercise_namespace.value = selectedScenario.value.exercise.namespace
    exercise_uuid.value = selectedScenario.value.exercise.uuid
    exercise_version.value = selectedScenario.value.exercise.version
    exercise_meta.value = JSON.stringify(selectedScenario.value.exercise.meta, null, 4)
  }
}
</script>

<template>
  <div>
    <div>
      <div class="mb-4 flex flex-row-reverse gap-2">
        <button class="btn select-none" @click="designScenario()">
          <FontAwesomeIcon :icon="faPenRuler" class="fa-fw"></FontAwesomeIcon>Design Scenario
        </button>
        <button class="btn btn-success select-none" @click="saveScenario()" :disabled="!canBeSaved">
          <FontAwesomeIcon :icon="faSave" class="fa-fw"></FontAwesomeIcon>Save Scenario
        </button>
        <button class="btn btn-danger select-none" @click="cancel()">
          <FontAwesomeIcon :icon="faTimes" class="fa-fw"></FontAwesomeIcon>Cancel Changes
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

            <div>
              <label for="uuid" class="block text-gray-700 font-bold mb-2">Scenario UUID</label>
              <input
                type="text"
                v-model="exercise_uuid"
                class="shadow border w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                id="uuid"
                placeholder="e0e52134-f84c-4c18-ae19-b6bd3acbfef7"
                disabled
              />
            </div>

            <div>
              <label for="uuid" class="block text-gray-700 font-bold mb-2">Scenario Version</label>
              <input
                type="text"
                v-model="exercise_version"
                class="shadow border w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                id="uuid"
                placeholder="20240717"
                disabled
              />
            </div>
          </div>

          <div class="flex gap-6">
            <div class="basis-1/2">
              <label for="name" class="block text-gray-700 font-bold mb-2">Scenario Meta</label>
              <JsonEditorVue
                v-if="showEditor"
                v-model="exercise_meta"
                ref="editor"
                :mode="Mode.text"
                :mainMenuBar="false"
                :indentation="4"
                class="shadow-lg border w-full"
              />
            </div>
            <div class="basis-1/4">
              <label for="name" class="block text-gray-700 font-bold mb-2">Scenario Meta</label>
              <div class="border-slate-200 border p-3 rounded w-full">
                <div class="flex gap-1">
                  <span class="font-bold">
                    <FontAwesomeIcon :icon="faHashtag"></FontAwesomeIcon> Injects
                  </span>
                  <span class="ml-auto font-semibold">{{ injectCount }}</span>
                </div>
                <div class="flex gap-1">
                  <span class="font-bold">
                    <FontAwesomeIcon :icon="faHashtag"></FontAwesomeIcon> Inject Payloads
                  </span>
                  <span class="ml-auto font-semibold">{{ injectPayloadCount }}</span>
                </div>
                <div class="flex gap-1">
                  <span class="font-bold">
                    <FontAwesomeIcon :icon="faHashtag"></FontAwesomeIcon> Target Tools
                  </span>
                  <span
                    :class="`ml-auto font-semibold ${
                      injectTargetToolUsed.length > 0 ? '' : 'font-normal text-gray-400'
                    }`"
                    >{{
                      injectTargetToolUsed.length > 0 ? injectTargetToolUsed.join(', ') : '- none -'
                    }}</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
