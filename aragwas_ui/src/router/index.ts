import About from "@/components/about.vue";
import FAQ from "@/components/faq.vue";
import GeneDetail from "@/components/geneDetail.vue";
import Genes from "@/components/genes.vue";
import GwasHeatmap from "@/components/gwasHeatmap.vue";
import Home from "@/components/home.vue";
import PhenotypeDetail from "@/components/phenotypeDetail.vue";
import Phenotypes from "@/components/phenotypes.vue";
import Studies from "@/components/studies.vue";
import StudyDetail from "@/components/studyDetail.vue";
import TopAssociations from "@/components/topAssociations.vue";
import TopGenes from "@/components/topGenes.vue";
import Vue from "vue";
import Router from "vue-router";

Vue.use(Router);

function idToNumber(route: any): any {
  return {
    id: Number(route.params.id),
  };
}

function homeSearchParams(route: any): any {
  const page = route.query.page ? Number(route.query.page) : undefined;
  return { view: route.query.view, queryTerm: route.query.queryTerm, page };
}

export default new Router({
  routes: [
    {
      path: "/",
      name: "home",
      component: Home, props: homeSearchParams,
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
      path: "/faq",
      name: "FAQ",
      component: FAQ,
    },
    {
      path: "/about",
      name: "about",
      component: About,
    },
    {
      path: "/top-associations",
      name: "topAssociations",
      component: TopAssociations,
    },
    {
      path: "/top-genes",
      name: "topGenes",
      component: TopGenes,
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
    {
      path: "/map",
      name: "map",
      component: GwasHeatmap, props: true,
    },
  ],
});
