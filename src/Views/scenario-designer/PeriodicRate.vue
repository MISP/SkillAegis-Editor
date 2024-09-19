<script setup>
import { onMounted, ref, watch } from "vue";


const model = defineModel({ required: true })

const amount = ref(10)
const time_unit = ref('seconds')

const ALLOWED_TIME_UNIT = [
    'seconds',
    'minutes',
    'hours',
]

onMounted(() => {
    if (model.value > 3600 && model.value % 3600 === 0) {
        amount.value = model.value / 3600
        time_unit.value = 'hours'
    } else if (model.value > 60 && model.value % 60 === 0) {
        amount.value = model.value / 60
        time_unit.value = 'minutes'
    } else {
        amount.value = model.value
        time_unit.value = 'seconds'
    }
})

watch(time_unit, () => {
    model.value = transformTimeToSeconds()
})
watch(amount, () => {
    model.value = transformTimeToSeconds()
})

function transformTimeToSeconds() {
    if (time_unit.value === 'seconds') {
        return amount.value
    } else if (time_unit.value === 'minutes') {
        return amount.value * 60
    } else if (time_unit.value === 'hours') {
        return amount.value * 60 * 60
    }
}

</script>

<template>
    <span class="inline-flex flex-nowrap">
        <input
            type="number"
            min="0"
            max="9999"
            v-model="amount"
            class="shadow border font-mono w-full rounded-l py-1 px-2 max-w-20 text-gray-700 leading-tight focus:outline-none focus:border focus:border-slate-400"
        />
        <select
            v-model="time_unit"
            class="shadow border font-mono w-full rounded-r py-1 px-2 text-gray-700 bg-white leading-tight focus:outline-none focus:border focus:border-slate-400"
        >
            <option v-for="(unit) in ALLOWED_TIME_UNIT" :key="unit">{{ unit }}</option>
        </select>
    </span>
</template>