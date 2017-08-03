<template>
    <div >
        <v-layout column align-start>
            <v-flex xs12>
                <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
            </v-flex>
        </v-layout>
        <v-layout row-sm wrap column class="mt-4 pl-4 pr-4">
            <v-flex xs12 sm6 md4>
                <v-flex xs12>
                    <v-layout column>
                        <h5 class="mb-1">Description</h5>
                        <v-divider></v-divider>
                        <v-layout row wrap class="mt-4">
                            <v-flex xs5 md3 >Name:</v-flex><v-flex xs7 md9>{{ phenotypeName }}</v-flex>
                            <v-flex xs5 md3>Number of studies:</v-flex><v-flex xs7 md9 >{{ studyNumber }}</v-flex>
                            <v-flex xs5 md3>Average number of hits:</v-flex><v-flex xs7 mm9>{{ avgHitNumber }}</v-flex>
                            <v-flex xs5 md3>AraPheno link:</v-flex><v-flex xs7 mm9><a v-bind:href="araPhenoLink" target="_blank">{{ phenotypeName }}</a></v-flex>
                            <v-flex xs5 md3>Description:</v-flex><v-flex xs7 mm9>{{ phenotypeDescription }}</v-flex>
                        </v-layout>
                    </v-layout>
                </v-flex>
                <v-flex xs12 class="mt-4">
                    <v-tabs id="similar-tabs" grow scroll-bars >
                        <v-tabs-bar slot="activators">
                            <v-tabs-slider></v-tabs-slider>
                            <v-tabs-item href="#similar-tabs-studies" ripple class="grey lighten-4 black--text">
                                <div>List of Studies</div>
                            </v-tabs-item>
                            <v-tabs-item href="#similar-tabs-phenotypes" ripple class="grey lighten-4 black--text">
                                <div>Similar Phenotypes</div>
                            </v-tabs-item>
                        </v-tabs-bar>
                        <v-tabs-content id = "similar-tabs-studies">
                             <v-data-table
                                    v-bind:headers="studyColumns"
                                    v-bind:items="studies"
                                    hide-actions
                            >
                            <template slot="headerCell" scope="props">
                                    {{ props.header.text }}
                            </template>
                            <template slot="items" scope="props">
                                <td>
                                    <router-link :to="{name: 'studyDetail', params: { id: props.item.pk }}">{{ props.item.name }}
                                    </router-link>
                                </td>
                                <td  class="text-xs-right">{{ props.item.method }}</td>
                                <td  class="text-xs-right">{{ props.item.genotype }}</td>
                            </template>
                            </v-data-table>
                        </v-tabs-content>
                        <v-tabs-content id="similar-tabs-phenotypes" >
                            <v-data-table
                                    v-bind:headers="phenotypeColumns"
                                    v-bind:items="similarPhenotypes"
                                    hide-actions
                            >
                            <template slot="headerCell" scope="props">
                                    {{ props.header.text }}
                            </template>
                            <template slot="items" scope="props" >
                                    <td v-if="props.item.phenotype_id!=id">
                                        <router-link :to="{name: 'phenotypeDetail', params: { id: props.item.phenotype_id }}">{{ props.item.name }}
                                        </router-link>
                                    </td>
                                    <td v-if="props.item.phenotype_id!=id">
                                        {{ props.item.to_name }}
                                    </td>
                            </template>
                            </v-data-table>
                        </v-tabs-content>
                    </v-tabs>
                </v-flex>
            </v-flex>
            <v-flex xs12 sm6 md8>
                <h5 class="mb-1">Associations List</h5><v-divider></v-divider>
                <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields" :view="phenotypeView"></top-associations>
            </v-flex>
        </v-layout>
    </div>
</template>

<script lang="ts">
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import {loadAssociationsOfPhenotype, loadPhenotype, loadSimilarPhenotypes, loadStudiesOfPhenotype} from "../api";

    import Study from "../models/study";

    import Breadcrumbs from "./breadcrumbs.vue"
    import TopAssociationsComponent from "./topasso.vue"


    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
        components: {
            "breadcrumbs": Breadcrumbs,
            "top-associations": TopAssociationsComponent,
        },
    })
    export default class PhenotypeDetail extends Vue {
      @Prop({required: true})
      id: number;
      phenotypeName: string = "";
      studyNumber = 0;
      studyIDs = [];
      studies: Study[] = [];
      similarPhenotypes =  [];
      avgHitNumber = 0;
      phenotypeDescription: string = "";
      araPhenoLink: string = "";
      studyColumns = [{text: "Name", align: "left", value: "name"}, {text: "Genotype", value: "genotype"}, {text: "Method", value: "method"} ];
      phenotypeColumns = [{text: "Name", align: "left", value: "name"},{text: "Trait Ontology", align: "left", value: "to"}];

      breadcrumbs = [{text: "Home", href: "/"}, {text: "Phenotypes", href: "/phenotypes"}, {text: this.phenotypeName, href: "", disabled: true}];

      maf = ["1","1-5","5-10", "10"];
      mac = ["5"];
      annotation = ["ns", "s", "in", "i"];
      type = ["genic", "non-genic"];
      chr = ["1", "2","3","4","5"];
      hideFields = ["phenotype"];
      showControls = ["chr","maf","annotation","type","mac","significant"];
      filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, mac: this.mac, type: this.type, significant: "p"};
      phenotypeView = {name: "phenotype", phenotypeId: this.id, controlPosition: "right"};



      @Watch("id")
      onChangeId(val: number, oldVal: number) {
          this.loadData();
          this.phenotypeView = {name: "phenotype", phenotypeId: this.id, controlPosition: "right"};
      }
      created(): void {
        this.loadData();
      }
      mounted(): void {

      }

//    PHENOTYPE DATA LOADING
      _displayPhenotypeData(data): void {
        this.phenotypeName = data.name;
        this.phenotypeDescription = data.description;
        this.araPhenoLink = data.araphenoLink;
        this.breadcrumbs[2].text = data.name;
        this.studyNumber = data.studySet.length;
        this.studyIDs = data.studySet;
      }
      _displaySimilarPhenotypes(data): void {
          this.similarPhenotypes = data;
          // Need to check for available phenotypes on AraGWAS
      }
      loadData(): void {
        try {
            loadPhenotype(this.id).then(this._displayPhenotypeData).then(this.loadStudyList);
            loadSimilarPhenotypes(this.id).then(this._displaySimilarPhenotypes);
        } catch (err) {
            console.log(err);

        }
      }
      async loadStudyList(data) {
        this.studies = await loadStudiesOfPhenotype(this.id);
      }
    }
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    .breadcrumbsitem {
        font-size: 18pt;
    }

    .container {
        margin:0 auto;
        max-width: 1280px;
        width: 90%
    }

    ul.breadcrumbs {
        padding-left:0;
    }

    .banner-title h1 {
        font-size: 4.2rem;
        line-height: 110%;
        margin: 2.1rem 0 1.68rem 0;
    }
    .banner-subtext h5 {
        font-weight:300;
        color:black;
    }

    .table {
        width: 100%;
        max-width: 100%;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }

    @media only screen and (min-width: 601px) {
        .container {
            width:85%
        }
    }

    @media only screen and (min-width: 993px) {
        .container {
            width:70%;
        }
    }

</style>
