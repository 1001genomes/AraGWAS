import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/home'
import Studies from '@/components/studies'
import Results from '@/components/results'
import Althome from '@/components/althome'
import StudyDetail from '@/components/studyDetail'
import PhenotypeDetail from '@/components/phenotypeDetail'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Althome
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
    },
    {
      path: '/phenotype/:phenotypeId?',
      name: 'phenotypeDetail',
      component: PhenotypeDetail, props: true
    }
  ]
});
