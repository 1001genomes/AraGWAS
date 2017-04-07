import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/home'
import Studies from '@/components/studies'
import Results from '@/components/results'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/studies',
      name: 'studies',
      component: Studies
    },
    {
      path: '/results/:queryTerm?',
      name: 'results',
      component: Results, props: true
    }
  ]
});
