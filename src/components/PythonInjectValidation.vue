<script setup>
    import { faCircleQuestion } from '@fortawesome/free-solid-svg-icons'
    import PythonEditor from "@/components/PythonEditor.vue"

    const script = defineModel()
</script>

<template>
    <div>
        <code><span style="color: #708;">def</span> <span style="color: #00f;">evaluate</span>(data<sup title="Contains the data send by the tool."><FontAwesomeIcon :icon="faCircleQuestion" class="fa-fw text-gray-600"></FontAwesomeIcon></sup>: dict, context<sup title="Evaluation context containing data such as current user or queried data"><FontAwesomeIcon :icon="faCircleQuestion" class="fa-fw text-gray-600"></FontAwesomeIcon></sup>: dict) -> bool:</code>
        <PythonEditor
            v-model="script"
            :indentation="4"
            class="shadow-lg border w-full"
        ></PythonEditor>
    </div>
</template>