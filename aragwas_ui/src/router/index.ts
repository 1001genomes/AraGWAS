import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/home'
import Studies from '@/components/studies'
import Results from '@/components/results'
import Althome from '@/components/althome'
import StudyDetail from '@/components/studyDetail'


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
    },
    {
      path: '/althome/',
      name: 'althome',
      component: Althome, props: true
    },
    {
      path: '/study/:studyId?',
      name: 'studyDetail',
      component: StudyDetail, props: true
    }
  ]
});
