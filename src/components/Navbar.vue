<script setup>
import { selectedScenario, selectedScenarioUUID, store } from '@/store.js'
import { faCaretRight } from '@fortawesome/free-solid-svg-icons'
import NavLink from '@/components/NavLink.vue'
</script>

<template>
  <nav class="">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 border-b border-slate-600">
      <div class="flex h-16 items-center justify-between">
        <div class="flex items-center">
          <div class="">
            <div class="ml-10 flex space-x-4">
              <NavLink to="/scenarios/index" class="">Scenario List</NavLink>
              <NavLink
                :to="`/scenarios/overview/${selectedScenarioUUID}`"
                :title="`${
                  $route.meta.requiresScenarioSelection && selectedScenarioUUID
                    ? ''
                    : 'Select a scenario'
                }`"
                :class="`flex flex-col justify-center ${
                  $route.meta.requiresScenarioSelection && selectedScenarioUUID !== null
                    ? ''
                    : '!cursor-not-allowed opacity-60'
                }`"
              >
                <span class="self-start">Scenario Overview</span>
                <transition name="slide-fade-reverse" mode="out-in">
                  <div
                    v-if="selectedScenario !== null"
                    class="font-semibold text-2xs self-start leading-3"
                  >
                    <FontAwesomeIcon :icon="faCaretRight" class="fa-fw"></FontAwesomeIcon>
                    {{ selectedScenario?.exercise?.name }}
                  </div>
                </transition>
              </NavLink>
              <NavLink
                :to="`/scenarios/designer/${selectedScenarioUUID}`"
                :title="`${
                  $route.meta.requiresScenarioSelection && selectedScenarioUUID
                    ? ''
                    : 'Select a scenario'
                }`"
                :class="`flex flex-col justify-center ${
                  $route.meta.requiresScenarioSelection && selectedScenarioUUID !== null
                    ? ''
                    : '!cursor-not-allowed opacity-60'
                }`"
              >
                <span class="self-start">Scenario Designer</span>
                <transition name="slide-fade-reverse" mode="out-in">
                  <div
                    v-if="selectedScenario !== null"
                    class="font-semibold text-2xs self-start leading-3"
                  >
                    <FontAwesomeIcon :icon="faCaretRight" class="fa-fw"></FontAwesomeIcon>
                    {{ selectedScenario?.exercise?.name }}
                  </div>
                </transition>
              </NavLink>
              <NavLink :to="`/injects/tester`">Inject Tester</NavLink>
            </div>
          </div>
        </div>
        <div class="ml-auto">
          <div class="flex flex-col items-center mt-9">
            <span id="logo"></span>
            <span class="text-slate-400 mt-1">SkillAegis</span>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
#logo {
  background-image: url(@/assets/skillaegis-logo.svg);
  width: 48px;
  height: 48px;
  display: block;
  background-size: 48px;
}
</style>