<script setup>
import { computed, ref } from "vue"
import { faCaretDown, faTimes } from '@fortawesome/free-solid-svg-icons'

const model = defineModel({ required: true })
const search = ref('')
const isOpen = ref(false)

const emit = defineEmits(['open', 'close', 'select'])

const props = defineProps({
  options: {
    type: Array,
    required: true
  },
  multiple: {
    type: Boolean,
    default: false,
  },
  searchable: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  taggable: Boolean,
  labelTextGetter: {
    type: String,
    default: 'name',
  },
  disabled: Boolean,
  hideSelected: {
    type: Boolean,
    default: false,
  },
  id: {
    type: String,
    default: null
  },
})

const internalValues = computed(() => {
    return model.value ?
        (Array.isArray(model.value) ? model.value : [model.value]) :
        []
})

const filteredOptions = computed(() => {
    const normalizedSearch = (search.value || '').toLowerCase().trim()

    let options = props.options.concat()

    options = search.value.length > 0 ? options
        .filter((option) => getOptionLabel(option).includes(normalizedSearch))
        .sort((a, b) => getOptionLabel(a).length - getOptionLabel(b).length) : options
    
    if (props.hideSelected) {
        options = options.filter(
            (option) => !model.value.map((option) => getOptionLabel(option))
                .includes(getOptionLabel(option))
        )
    }

   return options
})

const showNoResults = computed(() => {
    return filteredOptions.value.length === 0
})

function toggle() {
    isOpen.value ? deactivate() : activate()
}

function activate() {
    if (isOpen.value || props.disabled) return
    isOpen.value = true
    emit('open', props.id)
}

function deactivate() {
    if (!isOpen.value) return
    isOpen.value = false
    search.value = ''
    emit('close', props.id)
}

function isOptionSelected(option) {
    return model.value.filter((selectedOption) => {
        return JSON.stringify(selectedOption) == JSON.stringify(option)
    }).length > 0
}

function select(option) {
    if (isOptionSelected(option)) return
    if (props.multiple) {
        model.value = model.value.concat([option])
    } else {
        model.value = [option]
    }
    emit('select', option, props.id)
    search.value = ''
    deactivate()
}

function removeElement(option) {
    if (props.disabled) return
    if (option.disabled) return
    model.value = model.value.filter((selectedOption) => {
        return JSON.stringify(selectedOption) != JSON.stringify(option)
    })
}

function updateSearch(newValue) {

}

function getOptionLabel(option) {
    return option[props.labelTextGetter]
}
</script>

<template>
    <div
        :tabindex="props.searchable ? -1 : 0"
        class="
            w-full min-w-60 relative
            shadow rounded cursor-pointer
            bg-slate-50 text-gray-700 leading-tight focus:outline-none
        "
        role="combobox"
        @mousedown="activate()"
        @focus="activate()"
        @blur="searchable ? false : deactivate()"
        @keyup.esc="console.log('esc') || deactivate()"
    >
        <div class="py-2 px-1 rounded border focus:border-slate-400">
            <div name="caret" class="absolute right-2 text-slate-600">
                <FontAwesomeIcon :icon="faCaretDown" class="fa-fw transition-transform" :class="isOpen ? 'fa-rotate-180' : ''"></FontAwesomeIcon>
            </div>
            <div class="block">
                <span
                    v-if="internalValues.length == 0"
                    @mousedown.prevent="toggle"
                    name="placeholder"
                    class="text-slate-600"
                >
                    <slot name="placeholder">
                    <span class="mx-2">{{ placeholder }}</span>
                    </slot>
                </span>
                <template v-if="props.multiple">
                    <template v-for="(value, index) of internalValues">
                        <slot name="tag" :option="value" :search="search" :remove="removeElement">
                            <span class="rounded-lg shadow bg-[#22d3ee] px-2 py-1 text-black text-sm font-semibold ml-2 select-none inline-block" :key="index">
                                <span v-text="getOptionLabel(value)"></span>
                                <i
                                    tabindex="1"
                                    @keypress.enter.prevent="removeElement(value)"
                                    @mousedown.stop="removeElement(value)"
                                >
                                    <FontAwesomeIcon :icon="faTimes" class=" ml-2 text-sm text-gray-500 hover:text-gray-800 cursor-pointer"></FontAwesomeIcon>
                                </i>
                            </span>
                        </slot>
                    </template>
                </template>
                <template v-else-if="!props.multiple && internalValues.length > 0">
                    <slot name="selected" :option="internalValues[0]" :search="search" :remove="removeElement">
                        <span class="px-2 py-1 text-black text-sm font-semibold ml-2 select-none">
                            <span v-text="getOptionLabel(internalValues[0])"></span>
                        </span>
                    </slot>
                </template>
            </div>
        </div>
        <div class="option-container">
            <input
                v-if="searchable"
                v-model="search"
                type="text"
                autocomplete="off"
                :spellcheck="false"
                :placeholder="props.placeholder"
                :value="search"
                @input="updateSearch($event.target.value)"
                @focus.prevent="activate()"
                @blur.prevent="deactivate()"
                @keyup.esc="deactivate()"
                class="input"
                :aria-controls="'listbox-'+props.id"
            />
            <Transition>
                <div
                    name="content-wrapper"
                    v-show="isOpen"
                    tabindex="-1"
                    @focus="activate"
                    @mousedown.prevent
                >
                    <ul class="border" role="listbox" :id="'listbox-'+props.id">
                        <li
                            v-for="(option, index) of filteredOptions"
                            :key="index"
                            class="px-3 py-2 first:pt-2 odd:bg-slate-50 even:bg-slate-100 hover:bg-[#22d3ee] cursor-pointer"
                            :class="isOptionSelected(option) ? 'disabled' : ''"
                            :id="props.id + '-' + index"
                            @click.stop="select(option)"
                            role="option"
                        >
                            <span
                                v-if="option"
                                class="option"
                            >
                                <slot name="option" :option="option" :search="search" :index="index">
                                    <span>{{ getOptionLabel(option) }}</span>
                                </slot>
                            </span>
                        </li>

                        <li v-show="showNoResults && search">
                            <span>
                                No elements found. Consider changing the search query.
                            </span>
                        </li>
                    </ul>
                </div>
            </Transition>
        </div>
    </div>
</template>

<style scoped>
li.disabled {
    @apply cursor-not-allowed text-slate-800 bg-gray-300;
}

.v-enter-active {
  @apply transition duration-100 ease-out;
}
.v-leave-active {
  @apply transition duration-100 ease-in;
}
.v-enter-from,
.v-leave-to {
  @apply -translate-y-1;
  @apply opacity-0;
}
</style>