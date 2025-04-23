<script setup>
    import { python } from '@codemirror/lang-python'

    const model = defineModel()
</script>

<template>
    <div id="editor-container" class="shadow-lg border w-full">
        <VueCodemirror
          v-model="model"
          placeholder="return True"
          :style="{ height: '400px' }"
          :extensions="[python()]"
        ></VueCodemirror>
    </div>
</template>

<style scoped>
#editor-container {
    background: #fff;
}
</style>