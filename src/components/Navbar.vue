<script setup>
import { selectedScenario, selectedScenarioUUID, store } from '@/store.js'
import { faCaretRight } from '@fortawesome/free-solid-svg-icons'
import NavLink from '@/components/NavLink.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const allRoutes = {}
router.getRoutes().forEach((route) => {
  allRoutes[route.name] = route
})
</script>

<template>
  <nav class="">
    <div class="mx-auto 2xl:max-w-7xl max-w-10xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between relative">
        <div class="flex items-center py-2 border-b border-slate-600">
          <div class="">
            <div class="mx-10 flex space-x-4">
              <NavLink to="/scenarios/index" class="">Scenario List</NavLink>
              <NavLink
                :to="`/scenarios/overview/${selectedScenarioUUID}`"
                :title="`${
                  allRoutes['Scenario Overview'].meta.requiresScenarioSelection &&
                  selectedScenarioUUID
                    ? ''
                    : 'Select a scenario'
                }`"
                :class="`flex flex-col justify-center ${
                  allRoutes['Scenario Overview'].meta.requiresScenarioSelection &&
                  selectedScenarioUUID !== null
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
                  allRoutes['Scenario Designer'].meta.requiresScenarioSelection &&
                  selectedScenarioUUID
                    ? ''
                    : 'Select a scenario'
                }`"
                :class="`flex flex-col justify-center ${
                  allRoutes['Scenario Designer'].meta.requiresScenarioSelection &&
                  selectedScenarioUUID !== null
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
        <div class="ml-auto mt-[24px] hidden sm:block">
          <div class="flex flex-col items-center mt-16">
            <span id="logo"></span>
            <span id="logo-text"></span>
            <span
              class="text-slate-800 mt-0.5 font-bold px-2 py-0.25 rounded-md bg-slate-300 select-none"
            >
              Editor
            </span>
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

#logo-text {
  margin-top: 0.6rem;
  width: 110px;
  height: 24px;
  display: block;
  background-repeat: no-repeat;
  background-size: initial;
  background-image: url(@/assets/skillaegis-text.svg);
  /* Forces color #94a3b8 */
  filter: invert(72%) sepia(6%) saturate(998%) hue-rotate(176deg) brightness(90%) contrast(84%);
}
</style>