import Vue from 'vue'
import Vuetify from 'vuetify'
import Router from 'vue-router'
import Home from '@/components/Home'

Vue.use(Vuetify)
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    }
  ]
})
