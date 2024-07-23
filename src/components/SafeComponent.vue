<script setup>
import { useRoute } from 'vue-router'
import Alert from './Alert.vue'
import { onErrorCaptured, ref, watch } from 'vue'

const renderingError = ref([])

onErrorCaptured((_error, instance) => {
  console.warn(_error)
  renderingError.value = [_error.message, _error.stack]
  return false
})

const props = defineProps({
  tobe: Object
})

const route = useRoute()
watch(
  () => route.name,
  () => {
    renderingError.value = []
  },
  { immediate: true }
)
</script>

<template>
  <Alert
    v-if="renderingError.length > 0"
    title="This page could not be displayed! That scenario is most probably malformed."
    :message="renderingError"
    variant="danger"
  ></Alert>
  <keep-alive v-else>
    <component :is="props.tobe" />
  </keep-alive>
</template>