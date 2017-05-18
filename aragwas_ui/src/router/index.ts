import Althome from '@/components/althome.vue';
import Home from '@/components/home.vue';
import HomeLayout from '@/components/homelayout.vue'
import PhenotypeDetail from '@/components/phenotypeDetail.vue';
import Results from '@/components/results.vue';
import Studies from '@/components/studies.vue';
import Phenotypes from '@/components/phenotypes.vue'
import StudyDetail from '@/components/studyDetail.vue';
import Vue from 'vue';
import Router from 'vue-router';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Althome,
    },
    {
      path: '/studies',
      name: 'studies',
      component: Studies,
    },
    {
      path: '/phenotypes',
      name: 'phenotypes',
      component: Phenotypes,
    },
    {
      path: '/results/:queryTerm?',
      name: 'results',
      component: Results, props: true,
    },
    {
      path: '/althome/',
      name: 'althome',
      component: Althome, props: true,
    },
    {
      path: '/study/:studyId?',
      name: 'studyDetail',
      component: StudyDetail, props: true,
    },
    {
      path: '/phenotype/:phenotypeId?',
      name: 'phenotypeDetail',
      component: PhenotypeDetail, props: true,
    },
    {
      path: '/layout/',
      name: 'layout',
      component: HomeLayout, props: true,
    },
  ],
});
