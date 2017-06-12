import GeneDetail from "@/components/geneDetail.vue";
import Genes from "@/components/genes.vue";
import Home from "@/components/home.vue";
import PhenotypeDetail from "@/components/phenotypeDetail.vue";
import Phenotypes from "@/components/phenotypes.vue";
import Results from "@/components/results.vue";
import Studies from "@/components/studies.vue";
import StudyDetail from "@/components/studyDetail.vue";
import TopAssociations from "@/components/topAssociations.vue";
import Vue from "vue";
import Router from "vue-router";

Vue.use(Router);

function idToNumber(route: any): any {
  return {
    id: Number(route.params.id),
  };
}

export default new Router({
  routes: [
    {
      path: "/",
      name: "home",
      component: Home, props: true,
    },
    {
      path: "/studies",
      name: "studies",
      component: Studies,
    },
    {
      path: "/phenotypes",
      name: "phenotypes",
      component: Phenotypes,
    },
    {
      path: "/genes",
      name: "genes",
      component: Genes,
    },
    {
      path: "/top-associations",
      name: "topAssociations",
      component: TopAssociations,
    },
    {
      path: "/results/:queryTerm?&:currentPage?",
      name: "results",
      component: Home, props: true,
    },
    {
      path: "/study/:id",
      name: "studyDetail",
      component: StudyDetail, props: idToNumber,
    },
    {
      path: "/phenotype/:id",
      name: "phenotypeDetail",
      component: PhenotypeDetail, props: idToNumber,
    },
    {
      path: "/gene/:geneId?",
      name: "geneDetail",
      component: GeneDetail, props: true,
    },
  ],
});
