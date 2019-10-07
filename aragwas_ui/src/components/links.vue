<template>
  <div class="mt-0">
    <v-parallax src="/static/img/ara2.jpg" height="80">
      <div class="section">
        <div class="container mt-2">
          <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
          <!-- <v-divider></v-divider> -->
        </div>
      </div>
    </v-parallax>
    <div class="container">
      <div class="section">
        <v-layout>
          <v-flex xs12 column>
            <h5 class="light pt-3">
              <i class="material-icons brown-text" style="font-size:20px">link</i> Useful Links to Imporant Resources and Websites
            </h5>
            <v-card v-for="link in links" :key="link.title">
              <v-card-text>
                <div class="pl-4 pt-3 pr-4">
                  <div style="width:80px;float:left">
                    <v-avatar size="60px">
                      <a target="_blank" :href="link.link">
                        <img
                          style="height:70px;padding:5px 5px;"
                          :src="link.image"
                          alt
                          class="circle"
                        />
                      </a>
                    </v-avatar>
                  </div>
                  <div style="width:80%;float:left">
                    <p class="title">
                      <a target="_blank" :href="link.link">{{ link.title }}</a>
                    </p>
                    <p class="black--text" v-html="link.description"></p>
                  </div>
                  <br style="clear:both;" />
                </div>
              </v-card-text>
            </v-card>
            <h5 class="light pt-5">
              <i class="material-icons brown-text" style="font-size:20px">link</i> Code and Issue Tracker
            </h5>
            <v-card>
              <v-card-text>
                <div class="pl-4 pt-3 pr-4">
                  <p class="title">
                    <a
                      target="_blank"
                      href="https://github.com/1001genomes/AraGWAS"
                    >AraGWASCaralog GitHub Release</a>
                  </p>
                  <p
                    class="black--text"
                  >Link to the AraGWAS GitHub Release, inlcuding code and issue tracker.</p>
                </div>
              </v-card-text>
            </v-card>
          </v-flex>
        </v-layout>
      </div>
    </div>
  </div>
</template>



<script lang="ts">
import Vue from "vue";
import { Component, Watch } from "vue-property-decorator";
import Breadcrumbs from "./breadcrumbs.vue";

@Component({
  components: {
    breadcrumbs: Breadcrumbs
  }
})
export default class Links extends Vue {
  breadcrumbs = [
    { text: "Home", href: "/" },
    { text: "Links", href: "/links", disabled: true }
  ];
  links = [
    {
      title: "AraPheno",
      description:
        "AraPheno is a public and manually curated database for phenotypes of <em>Arabidopsis thaliana</em>.",
      link: "https://arapheno.1001genomes.org",
      image: "/static/img/arapheno_logo.jpg"
    },
    {
      title: "1001 Genomes",
      description:
        "A Catalog of <em>Arabidopsis thaliana</em> Genetic Variation.",
      link: "http://1001genomes.org",
      image: "/static/img/1001_logo.png"
    },
    {
      title: "easyGWAS",
      description:
        "easyGWAS is a web-application for performing, analysing, visualising and comparing genome-wide association studies for any kind of model organism.",
      link: "https://easygwas.org",
      image: "/static/img/easygwas_logo.png",
    },
    {
      title: "GWA-Portal",
      description:
        "GWA-Portal is a web-application for performing, analysing and visualising and comparing genome-wide association studies for <em>Arabidopsis thaliana</em>.",
      link: "https://gwas.gmi.oeaw.ac.at/",
      image: "/static/img/gwaportal_logo.png",
    },
    {
      title: "AraPort",
      description:
        "Araport is a one-stop-shop for <em>Arabidopsis thaliana</em> genomics. Araport offers gene and protein reports with orthology, expression, interactions and the latest annotation, plus analysis tools, community apps, and web services..",
      link: "https://www.araport.org/",
      image: "/static/img/araport_logo.png",
    },
    {
      title: "TAIR",
      description:
        "The Arabidopsis Information Resource (TAIR) maintains a database of genetic and molecular biology data for the model higher plant <em>Arabidopsis thaliana</em>",
      link: "https://www.arabidopsis.org/",
      image: "/static/img/tair_logo.png",
    },
    {
      title: "EnsemblPlants",
      description:
        "The Ensembl genome annotation system, developed jointly by the EBI and the Wellcome Trust Sanger Institute, has been used for the annotation, analysis and display of vertebrate genomes since 2000. Since 2009, the Ensembl site has been complemented by the creation of five new sites, for bacteria, protists, fungi, plants and invertebrate metazoa, enabling users to use a single collection of (interactive and programatic) interfaces for accessing and comparing genome-scale data from species of scientific interest from across the taxonomy",
      link: "http://plants.ensembl.org/Arabidopsis_thaliana/Info/Index",
      image: "/static/img/ensembleplants_logo.png",
    },
  ];
}
</script>

<style scoped>
</style>
