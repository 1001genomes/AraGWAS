import About from "@/components/about.vue";
import AssociationDetail from "@/components/associationDetail.vue";
import DownloadCenter from "@/components/downloadCenter.vue";
import FAQ from "@/components/faq.vue";
import GeneDetail from "@/components/geneDetail.vue";
import Genes from "@/components/genes.vue";
import GwasHeatmap from "@/components/gwasHeatmap.vue";
import Home from "@/components/home.vue";
import Links from "@/components/links.vue";
import PhenotypeDetail from "@/components/phenotypeDetail.vue";
import Phenotypes from "@/components/phenotypes.vue";
import Studies from "@/components/studies.vue";
import StudyDetail from "@/components/studyDetail.vue";
import TopAssociations from "@/components/topAssociations.vue";
import TopGenes from "@/components/topGenes.vue";
import TopKOGenes from "@/components/topKOGenes.vue";
import TopKOMutations from "@/components/topKOMutations.vue";
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
      path: "/download-center",
      name: "downloadCenter",
      component: DownloadCenter,
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
      path: "/links",
      name: "links",
      component: Links,
    },
    {
      path: "/top-associations",
      name: "topAssociations",
      component: TopAssociations,
    },
    {
      path: "/top-ko-mutations",
      name: "topKOMutations",
      component: TopKOMutations,
    },
    {
      path: "/top-genes",
      name: "topGenes",
      component: TopGenes,
    },
    {
      path: "/top-ko-genes",
      name: "topKOGenes",
      component: TopKOGenes,
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
      path: "/study/:id/associations/:assocId",
      name: "associationDetail",
      component: AssociationDetail, props: function(route: any): any {
        return {
          id: Number(route.params.id),
          assocId: route.params.assocId,
        };
      },
    },
    {
      path: "/map",
      name: "map",
      component: GwasHeatmap, props: true,
    },
  ],
});
