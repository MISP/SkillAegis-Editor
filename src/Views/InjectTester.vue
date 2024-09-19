<script setup>
import { Mode } from 'vanilla-jsoneditor'
import {
  faScrewdriverWrench,
  faListCheck,
  faClock,
  faCircleExclamation,
  faTriangleExclamation,
  faCircleCheck,
  faClipboard
} from '@fortawesome/free-solid-svg-icons'
import JsonEditorVue from 'json-editor-vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { testInject as testInjectAPI, testJqPath as testJqPathAPI } from '@/api'

const props = defineProps({
  inject_evaluation: String
})

const ALLOWED_STRATEGIES = {
  data_filtering: 'Filter Event data',
  query_mirror: 'Perform the same query against MISP',
  query_search: 'Perform a search query on MISP and compare the returned result'
}
const ALLOWED_TARGET_TOOLS = {
  MISP: 'MISP'
}
const COMPARISION_OPERATOR_PER_TYPE = {
  string: {
    contains:
      'All values defined must be present in the data. Data will be split based on whitespace and lower-cased.',
    equals: 'The data must be equals to the value.',
    equals_any: 'At least one of the values must be present in the data.',
    regex: 'Perform a regex match on the data.',
    count:
      'count the length of the string and compare against the provided value.\n Accepted values are `[number]` or `[operator][number]`. Examples: 12, >3, <=2.'
  },
  list: {
    contains: 'All values defined must be present in the data.',
    equals: 'All values defined must exactly be present in the data.',
    'contains-regex': 'All regexes defined must exactly match in the data.',
    count:
      'count the amount of item and compare against the provided value.\n Accepted values are `[number]` or `[operator][number]`. Examples: 12, >3, <=2.'
  },
  object: {
    count:
      'count the amount of keys and compare against the provided value.\n Accepted values are `[number]` or `[operator][number]`. Examples: 12, >3, <=2.'
  }
}

const OUTCOME_SUCCESS = 1,
  OUTCOME_FAILED = 2,
  OUTCOME_PENDING = 3,
  OUTCOME_WAITING = 4

const route = useRoute()

const TEST_GROUP_COLORS = ['cyan', 'amber', 'blue', 'pink', 'violet', 'green']

const inject_eval = computed(() => JSON.parse(props.inject_evaluation || '{}'))
const test_error = ref(null)
const show_doc = ref(false)
const show_samples = ref(false)
const showModalTestJQ = ref(false)
const jq_tester_path = ref('')
const jq_tester_data = ref('{"Event": {"info": "My Event"}}')
const jq_tester_extract_type = ref('all')
const jq_tester_result = ref()
const jq_tester_valid_inputs = computed(
  () => jq_tester_data.value.length > 0 && jq_tester_path.value.length > 0
)

const target_tool = ref('MISP')
const evaluation_strategy = ref([])
const evaluation_params = ref('[]')

const data_filtering_data = ref('{}')
const query_mirror_url = ref('')
const query_mirror_method = ref('')
const query_search_url = ref('')
const query_search_method = ref('')
const query_search_payload = ref('{}')
const query_search_misp_url = ref('https://localhost/')
const query_search_misp_apikey = ref('FI4gCRghRZvLVjlLPLTFZ852x2njkkgPSz0zQ3E0')

function isValidJSON(text) {
  try {
    JSON.parse(text)
    return true
  } catch (e) {
    return false
  }
}
const data_filtering_data_valid = computed(() => {
  if (typeof data_filtering_data.value === 'object') {
    return true
  }
  return isValidJSON(data_filtering_data.value)
})
const payloads_valid = computed(() => {
  if (typeof evaluation_params.value !== 'object') {
    if (!isValidJSON(evaluation_params.value)) {
      return false
    }
  }
  if (evaluation_strategy.value == 'query_search') {
    if (typeof query_search_payload.value !== 'object') {
      if (!isValidJSON(query_search_payload.value)) {
        return false
      }
    }
  }
  return true
})
const testResult = ref({})
const test_outcome_state = computed(() => {
  const testResultData = testResult.value?.data
  if (testResultData?.outcome === OUTCOME_SUCCESS) {
    return OUTCOME_SUCCESS
  } else if (testResultData?.outcome === OUTCOME_FAILED) {
    return OUTCOME_FAILED
  } else if (testResultData === undefined || testResultData === null) {
    return OUTCOME_WAITING
  } else if (testResultData === 'Fetching') {
    return OUTCOME_PENDING
  }
})
const test_outcome_style = computed(() => {
  const style = {
    icon: '',
    color: '',
    title: ''
  }
  if (test_outcome_state.value == OUTCOME_SUCCESS) {
    style.icon = faCircleCheck
    style.color = 'green'
    style.title = 'Successful'
  } else if (test_outcome_state.value == OUTCOME_FAILED) {
    style.icon = faTriangleExclamation
    style.color = 'red'
    style.title = 'Failed'
  } else if (test_outcome_state.value == OUTCOME_PENDING) {
    style.icon = faCircleExclamation
    style.color = 'purple'
    style.title = 'Pending'
  } else if (test_outcome_state.value == OUTCOME_WAITING) {
    style.icon = faClock
    style.color = 'amber'
    style.title = 'Waiting'
  }
  return style
})
const test_outcome_info = ref([])

onMounted(() => {
  initForm()
})

watch(
  () => route.params,
  () => {
    initForm()
  }
)

watch(evaluation_strategy, () => {
  testResult.value = {}
})

onBeforeUnmount(() => {
  resetForm()
})

function resetForm() {
  target_tool.value = 'MISP'
  evaluation_strategy.value = ''
  evaluation_params.value = '[]'
  query_mirror_url.value = ''
  query_mirror_method.value = ''
  query_search_url.value = ''
  query_search_method.value = ''
  query_search_payload.value = ''
  // query_search_misp_url.value = 'https://localhost/'
  // query_search_misp_apikey.value = 'xWY4JqZOtoP0xuGWxeb74EuHhxcOnHhgYQHTcMsJ'
  data_filtering_data.value = '{}'
}

function initForm() {
  if (inject_eval.value?.parameters !== undefined && inject_eval.value?.parameters.length > 0) {
    evaluation_strategy.value = inject_eval.value?.evaluation_strategy || ''
    evaluation_params.value = inject_eval.value?.parameters || '[]'
    query_mirror_url.value = inject_eval.value?.evaluation_context?.query_context?.url || ''
    query_mirror_method.value =
      inject_eval.value?.evaluation_context?.query_context?.request_method || ''
    query_search_url.value = inject_eval.value?.evaluation_context?.query_context?.url || ''
    query_search_method.value =
      inject_eval.value?.evaluation_context?.query_context?.request_method || ''
    query_search_payload.value = inject_eval.value?.evaluation_context?.query_context?.payload || ''
    data_filtering_data.value = {}
  }
}

function parseJSONNoError(json) {
  if (typeof json === 'object') {
    return json
  }
  try {
    return JSON.parse(json)
  } catch (e) {
    return null
  }
}

async function testInject() {
  testResult.value = 'Fetching'
  const payload = {
    target_tool: target_tool.value,
    evaluation_strategy: evaluation_strategy.value,
    eval_params: parseJSONNoError(evaluation_params.value)
  }

  if (evaluation_strategy.value == 'data_filtering') {
    payload.test_data = parseJSONNoError(data_filtering_data.value)
  } else if (evaluation_strategy.value == 'query_mirror') {
    payload.query_mirror_url = query_mirror_url.value
    payload.query_mirror_method = query_mirror_method.value
    payload.query_mirror_payload = parseJSONNoError(evaluation_params.value)
  } else if (evaluation_strategy.value == 'query_search') {
    payload.query_search_url = query_search_url.value
    payload.query_search_method = query_search_method.value
    payload.query_search_payload = parseJSONNoError(query_search_payload.value)
    payload.query_search_misp_url = query_search_misp_url.value
    payload.query_search_misp_apikey = query_search_misp_apikey.value
  }

  try {
    test_error.value = null
    testResult.value = await testInjectAPI(payload)
  } catch (error) {
    test_error.value = error
  }
}

async function testJqPath() {
  jq_tester_result.value = undefined
  const payload = {
    path: jq_tester_path.value,
    data: JSON.parse(jq_tester_data.value),
    extract_type: jq_tester_extract_type.value
  }
  try {
    const result = await testJqPathAPI(payload)
    if (result.success === false) {
      jq_tester_result.value = JSON.stringify(result, undefined, 2)
    } else {
      jq_tester_result.value = JSON.stringify(result.data, undefined, 2)
    }
  } catch (error) {
    jq_tester_result.value = error
  }
}

function copyToClipboardFeedback(target, text) {
  target.classList.add('text-green-700')
  target.classList.remove('text-black')
  setTimeout(() => {
    target.classList.remove('text-green-700')
    target.classList.add('text-black')
  }, 1000)
  copyToClipboard(text)
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
}
</script>

<template>
  <div>
    <div
      class="flex flex-row flex-wrap items-center justify-between border border-slate-400 shadow-md rounded-lg px-3 pt-2 pb-4 mb-2 text-"
    >
      <div>
        <h3 class="text-lg">Evaluation Strategy</h3>
        <div class="flex flex-wrap gap-x-4 mt-2">
          <div
            class="relative flex w-56 items-center justify-center rounded-xl bg-gray-50 px-4 py-3 font-medium text-gray-700"
            v-for="(strategy_info, strategy) in ALLOWED_STRATEGIES"
            :key="strategy"
            :value="strategy"
          >
            <input
              v-model="evaluation_strategy"
              class="peer hidden"
              type="radio"
              name="radio_strategy"
              :value="strategy"
              :id="`radio_${strategy}`"
            />
            <label
              class="peer-checked:[#22d3ee] peer-checked:bg-[#def8fc] absolute top-0 h-full w-full cursor-pointer rounded-xl border peer-checked:border-[#22d3ee] hover:border-cyan-400"
              :title="strategy_info"
              :for="`radio_${strategy}`"
            >
            </label>
            <div
              class="peer-checked:border-transparent peer-checked:bg-[#22d3ee] peer-checked:ring-2 absolute left-4 h-5 w-5 rounded-full border-2 border-gray-300 bg-gray-200 ring-[#22d3ee] ring-offset-2"
            ></div>
            <span class="pointer-events-none z-10">{{ strategy }}</span>
          </div>
        </div>
      </div>

      <div class="min-w-60">
        <label for="target_tool" class="block text-lg mb-1">
          <FontAwesomeIcon :icon="faScrewdriverWrench" class="fa-fw"></FontAwesomeIcon>
          Target Tool
        </label>
        <select
          v-model="target_tool"
          class="shadow border w-full rounded py-2 px-2 text-gray-700 leading-tight focus:outline-none focus:border-slate-400 bg-white"
          id="target_tool"
          placeholder="MISP"
          disabled
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

    <div class="flex gap-3 mt-8">
      <div class="basis-3/5">
        <Transition name="slide-right-fade" mode="out-in">
          <div v-if="evaluation_strategy == 'data_filtering'" class="flex flex-col gap-2">
            <h3 class="text-lg">Data Filtering</h3>
          </div>

          <div v-else-if="evaluation_strategy == 'query_mirror'" class="flex flex-col gap-2">
            <h3 class="text-lg">Query Mirror</h3>

            <Alert
              title="Impossible to test query_mirror strategy"
              variant="warning"
              message="There is no point to test this strategy at the moment."
            ></Alert>
            <div class="flex flex-col gap-2 relative p-2">
              <div
                class="absolute left-0 top-0 w-full h-full z-30 backdrop-blur-[2px] bg-slate-300/30 rounded box-content"
              ></div>
              <div class="ml-5">
                <div class="font-semibold pt-1 text-nowrap">URL</div>
                <div class="min-w-60">
                  <input
                    type="text"
                    v-model="query_mirror_url"
                    class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                    placeholder="Data created"
                  />
                </div>
              </div>
              <div class="ml-5">
                <div class="font-semibold pt-1 text-nowrap">Request Method</div>
                <div class="min-w-60">
                  <input
                    type="text"
                    v-model="query_mirror_method"
                    class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                    placeholder="Data created"
                  />
                </div>
              </div>
              <div class="ml-5">
                <div class="font-semibold pt-1 text-nowrap">Request Payload</div>
                <div class="min-w-60">
                  <JsonEditorVue
                    v-model="evaluation_params"
                    :mode="Mode.text"
                    :mainMenuBar="false"
                    :indentation="4"
                    class="shadow border w-full"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="evaluation_strategy == 'query_search'" class="flex flex-col gap-2">
            <h3 class="text-lg">Query Search</h3>
            <div class="ml-5">
              <div class="font-semibold pt-1 text-nowrap">URL</div>
              <div class="min-w-60">
                <input
                  type="text"
                  v-model="query_search_url"
                  class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                  placeholder="Data created"
                />
              </div>
            </div>
            <div class="ml-5">
              <div class="font-semibold pt-1 text-nowrap">Request Method</div>
              <div class="min-w-60">
                <input
                  type="text"
                  v-model="query_search_method"
                  class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                  placeholder="Data created"
                />
              </div>
            </div>
            <div class="ml-5">
              <div class="font-semibold pt-1 text-nowrap">Request Payload</div>
              <div class="min-w-60">
                <JsonEditorVue
                  v-model="query_search_payload"
                  :mode="Mode.text"
                  :mainMenuBar="false"
                  :indentation="4"
                  class="shadow border w-full"
                />
              </div>
            </div>
          </div>
        </Transition>

        <div v-if="evaluation_strategy != 'query_mirror'" class="ml-5 mt-2">
          <div class="font-semibold pt-1 text-nowrap">Evaluation Parameters</div>
          <JsonEditorVue
            v-model="evaluation_params"
            :mode="Mode.text"
            :mainMenuBar="false"
            :indentation="4"
            class="shadow border w-full"
          />
        </div>
      </div>

      <div class="basis-2/5 flex flex-col gap-3 relative p-2">
        <div
          v-if="evaluation_strategy == 'query_mirror'"
          class="absolute left-0 top-0 w-full h-full z-30 backdrop-blur-[2px] bg-slate-300/30 rounded box-content"
        ></div>
        <div class="rounded shadow-md bg-white">
          <div class="text-lg bg-slate-600 shadow px-4 py-2 text-gray-50 rounded-t">
            Test Inject
          </div>

          <div class="p-4 box-border">
            <Transition name="slide-left-fade" mode="out-in">
              <div v-if="evaluation_strategy == 'data_filtering'" class="mb-4">
                <div class="font-semibold text-nowrap">Test Data</div>
                <div class="min-w-60">
                  <JsonEditorVue
                    v-model="data_filtering_data"
                    :mode="Mode.text"
                    :mainMenuBar="false"
                    :indentation="4"
                    class="shadow-md border w-full max-h-96 overflow-auto"
                  />
                </div>
              </div>
              <div v-else-if="evaluation_strategy == 'query_search'" class="mb-4">
                <div class="flex flex-col gap-2">
                  <div>
                    <div class="font-semibold pt-1 text-nowrap">MISP URL</div>
                    <div class="min-w-60">
                      <input
                        type="text"
                        v-model="query_search_misp_url"
                        class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                        placeholder="https://misp.local"
                      />
                    </div>
                  </div>
                  <div>
                    <div class="font-semibold pt-1 text-nowrap">MISP API Key</div>
                    <div class="min-w-60">
                      <input
                        type="text"
                        v-model="query_search_misp_apikey"
                        class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                        placeholder="FI4gCRghRZvLVjlLPLTFZ852x2njkkgPSz0zQ3E0"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
            <button
              class="btn btn-block btn-info btn-colored select-none mb-2"
              @click="testInject()"
              :disabled="
                evaluation_strategy == 'query_mirror' ||
                !(data_filtering_data_valid && payloads_valid)
              "
            >
              <FontAwesomeIcon :icon="faListCheck" class="fa-fw"></FontAwesomeIcon> Test Inject
            </button>

            <div class="my-2 select-none">
              <span class="font-semibold inline-block w-[5.5rem]">Outcome</span>
              <span>
                <span
                  :class="`px-2 py-1 rounded-lg bg-${test_outcome_style.color}-100 text-${test_outcome_style.color}-800 shadow transition-colors`"
                >
                  <FontAwesomeIcon :icon="test_outcome_style.icon" class="mr-2"></FontAwesomeIcon>
                  <span class="font-semibold">{{ test_outcome_style.title }}</span>
                </span>
              </span>
            </div>
            <div>
              <span
                v-if="testResult.data?.debug || test_error != null"
                class="font-semibold select-none inline-block w-[5.5rem]"
                >Debug</span
              >
              <span v-if="test_error != null">
                <pre>{{ test_error }}</pre>
              </span>
              <div v-if="testResult.data?.debug" class="flex-auto p-2">
                <div
                  v-for="(testGroup, i) in testResult.data.debug"
                  :key="i"
                  class="relative flex flex-col mb-5"
                >
                  <div
                    v-for="(entry, j) in testGroup"
                    :key="j"
                    class="relative flex flex-col justify-center"
                  >
                    <div
                      :class="`absolute left-4 ${
                        j < testGroup.length - 1 ? 'h-full' : 'h-2/3 top-0 w-2 border-b-2'
                      } border-l-2`"
                    ></div>
                    <div class="relative mb-2">
                      <span
                        v-if="j == 0"
                        :class="`absolute select-none inline-flex h-6 w-6 items-center justify-center rounded-full bg-${TEST_GROUP_COLORS[i]}-500 p-4 text-center text-base font-semibold text-white shadow`"
                        >{{ i + (evaluation_strategy == 'query_mirror' ? 0 : 1) }}</span
                      >
                      <div class="ml-12 w-auto pt-1">
                        <h6
                          v-if="entry.style == 'primary'"
                          :class="`text-sm font-bold text-${TEST_GROUP_COLORS[i]}-900`"
                        >
                          {{ entry.message }}
                        </h6>
                        <h6
                          v-else
                          :class="`text-sm font-semibold text-${TEST_GROUP_COLORS[i]}-900`"
                        >
                          <span
                            v-if="
                              entry.style == 'success' ||
                              entry.style == 'fail' ||
                              entry.style == 'error'
                            "
                          >
                            <span
                              :class="`text-xs mr-1 px-2 py-1 rounded-lg bg-${
                                entry.style == 'success' ? 'green' : 'red'
                              }-100 text-${entry.style == 'success' ? 'green' : 'red'}-800 shadow`"
                            >
                              <FontAwesomeIcon
                                :icon="
                                  entry.style == 'success'
                                    ? faCircleCheck
                                    : entry.style == 'error'
                                    ? faCircleExclamation
                                    : faTriangleExclamation
                                "
                                class="mr-2"
                              ></FontAwesomeIcon>
                              <span class="font-semibold capitalize">{{ entry.style }}</span>
                            </span>
                          </span>
                          {{ entry.message }}
                        </h6>
                        <p class="mt-1 text-sm text-gray-500">
                          <span
                            v-if="
                              typeof entry.data !== 'object' ||
                              entry.data === null ||
                              Object.keys(entry.data).length > 0
                            "
                          >
                            <pre
                              :class="`text-xs max-h-32 overflow-y-auto whitespace-pre-wrap ${
                                typeof entry.data === 'object'
                                  ? 'mt-2 p-1 rounded-sm bg-slate-100 border border-slate-200'
                                  : ''
                              }`"
                              >{{ JSON.stringify(entry.data, undefined, 2).slice(0, 15000) }}</pre
                            >
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6">
      <div class="rounded shadow-md bg-white">
        <div class="bg-slate-600 shadow px-4 py-2 text-gray-50 rounded-t">Documentation</div>
        <div class="px-3 py-2">
          <div>
            <button class="btn select-none mb-2" @click="showModalTestJQ = true">
              Test <code class="text-gray-500">./jq</code> path
            </button>

            <Modal :showModal="showModalTestJQ" @modal-close="showModalTestJQ = false">
              <template #header>Test <code class="text-gray-500">./jq</code> path</template>
              <template #body>
                <div class="">
                  <div class="font-semibold pt-1 text-nowrap">Data</div>
                  <div class="min-w-60">
                    <JsonEditorVue
                      v-model="jq_tester_data"
                      :mode="Mode.text"
                      :mainMenuBar="false"
                      :indentation="4"
                      class="shadow border w-full max-h-60 overflow-auto"
                    />
                  </div>
                </div>
                <div class="mt-2">
                  <div class="font-semibold pt-1 text-nowrap">
                    <code class="text-gray-500">./jq</code> Path
                  </div>
                  <div class="min-w-60">
                    <input
                      type="text"
                      v-model="jq_tester_path"
                      class="shadow border font-mono w-full rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
                      placeholder=".Event.info"
                      @keypress.enter="jq_tester_valid_inputs && testJqPath()"
                    />
                  </div>
                </div>
                <div class="mt-2">
                  <div class="font-semibold pt-1 text-nowrap">Extract Type</div>
                  <div class="inline-flex gap-1">
                    <input type="radio" id="first" value="first" v-model="jq_tester_extract_type" />
                    <label for="first">First</label>
                  </div>

                  <div class="inline-flex gap-1 ml-3">
                    <input type="radio" id="all" value="all" v-model="jq_tester_extract_type" />
                    <label for="all">All</label>
                  </div>
                </div>
                <div class="mt-2">
                  <button
                    class="btn btn-block btn-info btn-colored select-none my-2"
                    @click="testJqPath()"
                    :disabled="!jq_tester_valid_inputs"
                  >
                    Test
                    <code :class="jq_tester_valid_inputs ? 'text-gray-200' : 'text-gray-500'"
                      >./jq</code
                    >
                    path
                  </button>
                </div>
                <div class="mt-2">
                  <div class="font-semibold pt-1 text-nowrap">Result</div>
                  <JsonEditorVue
                    v-model="jq_tester_result"
                    :mode="Mode.view"
                    :mainMenuBar="false"
                    :navigationBar="false"
                    :indentation="4"
                    class="shadow border w-full max-h-60 overflow-auto"
                    readOnly
                  />
                </div>
              </template>
            </Modal>
          </div>
          <Alert variant="info" title="Supported comparison operators per extracted data type">
            <template #message>
              <div>
                <div>
                  <label for="showdoc" class="cursor-pointer select-none">
                    <input id="showdoc" type="checkbox" v-model="show_doc" class="mr-1" /> Show
                    Documentation
                  </label>
                </div>
                <div v-show="show_doc">
                  <ul>
                    <li v-for="(info, type) in COMPARISION_OPERATOR_PER_TYPE" :key="type">
                      <span class="text-lg font-mono text-red-700">{{ type }}</span>
                      <ul class="ml-5 mb-2">
                        <li v-for="(text, operator) in info" :key="operator">
                          <span class="font-semibold font-mono">{{ operator }}:</span>
                          <span class="font-light ml-2 whitespace-break-spaces">{{ text }}</span>
                        </li>
                      </ul>
                    </li>
                  </ul>
                </div>
              </div>
            </template>
          </Alert>
          <Alert variant="info" title="MISP Format JQ samples">
            <template #message>
              <div>
                <div>
                  <label for="showsamples" class="cursor-pointer select-none">
                    <input id="showsamples" type="checkbox" v-model="show_samples" class="mr-1" />
                    Show Samples
                  </label>
                </div>
                <div v-show="show_samples">
                  <ul class="mt-2">
                    <li class="mb-3">
                      <span class="font-semibold">Get all Attributes:</span>
                      <span class="ml-1 text-sm italic"
                        >Creates an array combining all normal Attributes and Object's
                        Attributes</span
                      >
                      <div class="font-mono text-sm text-red-700 px-3 py-2 bg-slate-50 rounded">
                        <button
                          class="btn text-black"
                          @click="
                            copyToClipboardFeedback(
                              $event.currentTarget,
                              $event.currentTarget.parentElement.innerText
                            )
                          "
                        >
                          <FontAwesomeIcon :icon="faClipboard"></FontAwesomeIcon>
                        </button>
                        <pre class="inline-block ml-2 select-text">
[.Event.Object[].Attribute[], .Event.Attribute[]]</pre
                        >
                      </div>
                    </li>
                    <li class="mb-3">
                      <span class="font-semibold">Filter by Attribute's type:</span>
                      <span class="ml-1 text-sm italic"
                        >Collect normal Attributes then only keep <code>sha1</code> Attributes</span
                      >
                      <div class="font-mono text-sm text-red-700 px-3 py-2 bg-slate-50 rounded">
                        <button
                          class="btn text-black"
                          @click="
                            copyToClipboardFeedback(
                              $event.currentTarget,
                              $event.currentTarget.parentElement.innerText
                            )
                          "
                        >
                          <FontAwesomeIcon :icon="faClipboard"></FontAwesomeIcon>
                        </button>
                        <pre class="inline-block ml-2 select-text">
.Event.Attribute[] | select(.type == \"sha1\")</pre
                        >
                      </div>
                    </li>
                    <li class="">
                      <span class="font-semibold"
                        >Filter by Object's name and Attribute's type:</span
                      >
                      <span class="ml-1 text-sm italic"
                        >Collect all <code>URL</code> Objects and then only keep
                        <code>sha1</code> Attributes</span
                      >
                      <div class="font-mono text-sm text-red-700 px-3 py-2 bg-slate-50 rounded">
                        <button
                          class="btn text-black"
                          @click="
                            copyToClipboardFeedback(
                              $event.currentTarget,
                              $event.currentTarget.parentElement.innerText
                            )
                          "
                        >
                          <FontAwesomeIcon :icon="faClipboard"></FontAwesomeIcon>
                        </button>
                        <pre class="inline-block ml-2 select-text">
.Event.Object[] | select((.name == \"url\")).Attribute[] | select(.type == \"url\").value</pre
                        >
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </template>
          </Alert>
        </div>
      </div>
    </div>
  </div>
</template>