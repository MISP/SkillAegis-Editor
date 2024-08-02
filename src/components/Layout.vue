<script setup>
import { selectedScenario, selectedScenarioUUID } from '@/store.js'
import { faCaretRight } from '@fortawesome/free-solid-svg-icons'
import Toaster from '@/components/Toaster.vue'
import Navbar from '@/components/Navbar.vue'
import SafeComponent from '@/components/SafeComponent.vue'
</script>

<template>
  <div class="flex flex-col">
    <div class="bg-slate-800 pb-[6rem]">
      <Navbar></Navbar>

      <header class="shadow">
        <div class="mx-auto w-11/12 max-w-10xl py-8 px-4">
          <h1 class="text-3xl font-bold tracking-tight text-white select-none">
            {{ $route.name }}
            <span v-show="$route.name !== 'Scenarios List' && selectedScenario !== null">
              <FontAwesomeIcon :icon="faCaretRight" class="fa-fw"></FontAwesomeIcon>
              <span class="font-light">{{ selectedScenario?.exercise?.name }}</span>
            </span>
          </h1>
        </div>
      </header>
    </div>

    <main class="flex-auto">
      <div
        class="min-h-[800px] mx-auto -mt-[7rem] mb-4 w-11/12 max-w-10xl px-6 py-6 h-full bg-slate-50 rounded-lg"
      >
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <SafeComponent :tobe="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <Toaster></Toaster>
  </div>
</template>