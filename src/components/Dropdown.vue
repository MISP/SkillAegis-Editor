<script setup>
import { computed, nextTick, ref, watch } from "vue"
import { faCaretDown, faTimes } from '@fortawesome/free-solid-svg-icons'

const model = defineModel({ required: true })
const search = ref('')
const isOpen = ref(false)
const searchbox = ref()
const selectbox = ref()

watch(isOpen, async (dropdownOpen) => {
    if (dropdownOpen) {
        await nextTick()
        if (props.searchable) {
            searchbox.value.focus()
        } else {
            selectbox.value.focus()
        }
    }
})

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
  taggable: {
    type: Boolean,
    validator(value, props) {
        return value && props.searchable
    }
  },
  labelTextGetter: {
    type: String,
    default: 'label',
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

const optionsAreObjects = computed(() => {
    if (props.options.length == 0) {
        return false
    }
    return typeof props.options[0] !== 'string'
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
        .filter((option) => getOptionLabel(option).toLowerCase().includes(normalizedSearch))
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
        search.value = ''
        deactivate()
    }
    emit('select', option, props.id)
}

function removeElement(option) {
    if (props.disabled) return
    if (option.disabled) return
    model.value = model.value.filter((selectedOption) => {
        return JSON.stringify(selectedOption) != JSON.stringify(option)
    })
}

function addNewTagElement() {
    if (props.disabled) return
    if (!props.taggable) return

    if (filteredOptions.value.length == 0) {
        let newOption = search.value
        if (optionsAreObjects.value) {
            newOption = {value: search.value}
            newOption[props.labelTextGetter] = search.value
        }
        select(newOption)
        search.value = ''
    }
}


function getOptionLabel(option) {
    return typeof option === 'string' ? option : option[props.labelTextGetter]
}
</script>

<template>
    <div
        ref="selectbox"
        tabindex="0"
        class="
            w-full min-w-60 relative
            shadow rounded cursor-pointer
            bg-slate-50 text-gray-700 leading-tight focus:outline-none
        "
        role="combobox"
        @mousedown="activate()"
        @focus="activate()"
        @blur="searchable ? false : deactivate()"
        @keyup.esc="deactivate()"
    >
        <div class="py-1.5 px-1 rounded border focus:border-slate-400 flex items-center">
            <div name="caret" class="absolute right-2 text-slate-600">
                <FontAwesomeIcon :icon="faCaretDown" class="fa-fw transition-transform" :class="isOpen ? 'fa-rotate-180' : ''"></FontAwesomeIcon>
            </div>
            <div class="block min-h-7 content-center">
                <span
                    v-if="internalValues.length == 0"
                    @mousedown.prevent="toggle"
                    name="placeholder"
                    class="text-slate-600 text-"
                >
                    <slot name="placeholder">
                    <span class="mx-2 select-none">{{ placeholder }}</span>
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
            <Transition>
                <div
                name="content-wrapper"
                v-show="isOpen"
                tabindex="-1"
                @focus="activate()"
                >
                <ul class="border shadow-md" role="listbox" :id="'listbox-'+props.id">
                    <li>
                            <input
                                v-if="props.searchable"
                                ref="searchbox"
                                v-model="search"
                                type="text"
                                autocomplete="off"
                                :spellcheck="false"
                                placeholder="Search an option"
                                @focus.prevent="activate()"
                                @blur.prevent="deactivate()"
                                @keyup.esc="deactivate()"
                                @keypress.enter.prevent.stop.self="addNewTagElement()"
                                class="w-full px-3 py-2 text-cyan-800 shadow-inner border-b border-gray-200 outline-none"
                                :aria-controls="'listbox-'+props.id"
                            />
                        </li>
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

                        <li v-show="showNoResults && search" class="bg-slate-50">
                            <span class="inline-block m-1 px-2 py-1 rounded bg-amber-500 text-black">
                                No elements found.
                                <span v-if="!props.taggable">
                                    Consider changing the search query.
                                </span>
                            </span>
                            <span v-if="props.taggable" class="inline-block m-1 px-2 py-1 ml-1 rounded bg-blue-700 text-white text-center">
                                Press <code class="inline align-middle text-xs rounded-sm bg-white text-red-900 px-1 py-0.5 mx-1">&lt;enter&gt;</code> to create a new option.
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
    @apply cursor-not-allowed;
    @apply text-slate-800 bg-gray-300;
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