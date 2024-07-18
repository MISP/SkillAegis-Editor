<template>
  <RouterLink
    v-bind="$attrs"
    class="cursor-pointer flex items-center rounded-md h-12 px-3 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700 hover:text-white"
    active-class="bg-blue-800 text-white"
    inactive-class="text-slate-300 hover:bg-slate-700 hover:text-white"
  >
    <slot />
  </RouterLink>
</template>