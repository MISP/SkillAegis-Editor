<script setup>
import { faHashtag } from '@fortawesome/free-solid-svg-icons'
import { selectedScenario as originalSelectedScenario } from '@/store.js'
import { computed, ref } from 'vue'

const selectedScenario = computed(() => {
  return originalSelectedScenario.value !== null
    ? JSON.parse(JSON.stringify(originalSelectedScenario.value))
    : null
})

const inject_flow = computed(() => {
  return selectedScenario.value?.inject_flow || []
})

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

const dependencies = computed(() => {
  const requirements = {}
  inject_flow.value.forEach((injF) => {
    requirements[injF.inject_uuid] = []
  })
  inject_flow.value.forEach((injF) => {
    if (
      injF.requirements.inject_uuid !== undefined &&
      injF.requirements.inject_uuid !== null &&
      injF.requirements.inject_uuid.length > 0
    ) {
      if (requirements[injF.requirements.inject_uuid] === undefined) {
        console.warn(`Inject flow ${injF.inject_uuid} required requirement ${injF.requirements.inject_uuid} but this inject doesn't exist.`)
      } else {
        requirements[injF.requirements.inject_uuid].push(injF.inject_uuid)
      }
    }
  })
  return requirements
})

const hoveredInjectUUID = ref(null)
</script>

<template>
  <div>
    <label for="name" class="block text-gray-700 font-bold mb-2">Inject dependencies</label>
    <div class="border-slate-200 border p-3 rounded w-full bg-white">
      <div>
        <table class="w-full group">
          <thead>
            <tr>
              <th class="text-left"></th>
              <th class="text-left">Inject</th>
              <th class="text-left px-2">Requires Completion</th>
              <th class="text-left">Dependent Injects</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(injF, i) in inject_flow" :key="injF.inject_uuid">
              <td class="py-1 px-2 text-slate-500 text-sm select-none">
                <FontAwesomeIcon :icon="faHashtag"></FontAwesomeIcon> {{ i + 1 }}
              </td>
              <td class="py-1 px-2">
                <a
                  @mouseover="hoveredInjectUUID = injF.inject_uuid"
                  @mouseleave="hoveredInjectUUID = null"
                  :class="`text-nowrap select-none px-1 py-0.5 border border-slate-300 rounded ${
                    hoveredInjectUUID == injF.inject_uuid ? 'highlighted-inject' : ''
                  }`"
                  >{{ injectByUUID[injF.inject_uuid].name }}</a
                >
              </td>
              <td class="py-1 px-2">
                <span
                  v-if="
                    injectFlowByUUID[injF.inject_uuid].requirements?.inject_uuid === undefined ||
                    injectFlowByUUID[injF.inject_uuid].requirements?.inject_uuid === null
                  "
                  class="text-slate-500 text-sm select-none"
                  >- no requirements -</span
                >
                <div v-else>
                  <a
                    @mouseover="
                      hoveredInjectUUID =
                        injectFlowByUUID[injF.inject_uuid].requirements?.inject_uuid
                    "
                    @mouseleave="hoveredInjectUUID = null"
                    :class="`text-nowrap select-none px-1 py-0.5 border border-slate-300 rounded ${
                      hoveredInjectUUID ==
                      injectFlowByUUID[injF.inject_uuid].requirements?.inject_uuid
                        ? 'highlighted-inject'
                        : ''
                    }`"
                    >{{
                      injectByUUID[injectFlowByUUID[injF.inject_uuid].requirements?.inject_uuid]
                        ?.name
                    }}</a
                  >
                </div>
              </td>
              <td class="py-1 px-2">
                <span
                  v-if="dependencies[injF.inject_uuid].length == 0"
                  class="text-slate-500 text-sm select-none"
                  >- no dependencies -</span
                >
                <div class="flex flex-col gap-1">
                  <div v-for="uuid in dependencies[injF.inject_uuid]" :key="uuid" class="">
                    <a
                      @mouseover="hoveredInjectUUID = uuid"
                      @mouseleave="hoveredInjectUUID = null"
                      :class="`text-nowrap select-none px-1 py-0.5 border border-slate-300 rounded ${
                        hoveredInjectUUID == uuid ? 'highlighted-inject' : ''
                      }`"
                      >{{ injectByUUID[uuid].name }}</a
                    >
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style>
.highlighted-inject {
  @apply bg-blue-100 border-blue-600;
}
</style>
