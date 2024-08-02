import './assets/main.css'

import { createWebHashHistory, createRouter } from 'vue-router'

// import HomeView from './HomeView.vue'
// import AboutView from './AboutView.vue'
import ScenarioList from './Views/ScenarioList.vue'
import ScenarioOverview from './Views/ScenarioOverview.vue'
import ScenarioNew from './Views/ScenarioNew.vue'
import ScenarioDesigner from './Views/ScenarioDesigner.vue'
import InjectTester from './Views/InjectTester.vue'

import { hasScenario, hasScenarios, store } from './store.js'

import { createApp, ref } from 'vue'
import App from './App.vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import Alert from '@/components/Alert.vue'
import Modal from '@/components/Modal.vue'
import { fetchScenarios } from './api'


const routes = [
    { path: '/scenarios/index', name: 'Scenario Index', component: ScenarioList, meta: { requiresScenarioSelection: false }, },
    { path: '/scenarios/add', name: 'New Scenario', component: ScenarioNew, meta: { requiresScenarioSelection: false }, },
    { path: '/scenarios/overview/:uuid?', name: 'Scenario Overview', component: ScenarioOverview, meta: { requiresScenarioSelection: true }, props: true },
    { path: '/scenarios/designer/:uuid?', name: 'Scenario Designer', component: ScenarioDesigner, meta: { requiresScenarioSelection: true }, props: true },
    { path: '/injects/tester/:inject_evaluation?', name: 'Inject Tester', component: InjectTester, props: true },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

router.beforeEach(async (to, from) => {
    if (to.path === '/') {
        return { path: '/scenarios/index' }
    }
    if (!hasScenarios()) {
        fetchScenarios()
    }
    if (from.name == undefined && ['Scenario Overview', 'Scenario Designer'].includes(to.name) && to?.params?.uuid !== undefined) {
        store.selected_scenario = to.params.uuid
    }
    if (to?.meta?.requiresScenarioSelection === true && store.selected_scenario === null) {
        return { path: '/scenarios/index' }
    }
    if (to.matched.length == 0) {
        return { path: '/scenarios/index' }
    }
    // if (to.path !== '/' && to.path !== '/scenarios') {
    //     if (store.selected_scenario === null) {
    //         return { path: '/scenarios' }
    //     }
    // }
})

let toastID = 0
export const toastBuffer = ref([])
export function toast(toast) {
    toastID += 1
    toast.id = toastID
    toastBuffer.value.push(toast)
}
export function removeToast(id) {
    toastBuffer.value = toastBuffer.value.filter((toast) => toast.id != id)
}
export function ajaxFeedback(response) {
    toast({
        variant: response.success ? 'success' : 'danger',
        message: String(response.message),
        title: response.title,
    })
}

const app = createApp(App)
app.component('FontAwesomeIcon', FontAwesomeIcon)
app.component('Alert', Alert)
app.component('Modal', Modal)
app.use(router)
app.mount('#app')