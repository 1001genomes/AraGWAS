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
                    <v-tabs id="similar-tabs" grow scroll-bars v:model="currentView">
                        <v-tabs-bar slot="activators">
                            <v-tabs-slider></v-tabs-slider>
                            <v-tabs-item :href="'#' + i" ripple class="grey lighten-4 black--text"
                                    v-for="i in ['List of Studies', 'Similar Phenotypes']" :key="i">
                                    <div>{{ i }}</div>
                                </v-tabs-item>
                        </v-tabs-bar>
                        <v-tabs-content :id="i" v-for="i in ['List of Studies','Similar Phenotypes']" :key="i">
                            <v-card>
                                <table class="table">
                                    <thead>
                                    <tr>
                                        <th v-for="key in columnsTab[i]"
                                            @click="sortBy(key)"
                                            :class="{ active: sortKey == key }">
                                            {{ key | capitalize }}
                                        </th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="entry in filteredStudiesAndPhenotypes">
                                            <td v-for="key in columnsTab[i]">
                                                <router-link v-if="(key==='study' && currentView === 'List of Studies')" :to="{name: 'studyDetail', params: { id: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='name' && currentView === 'Similar Phenotypes')" :to="{name: 'phenotypeDetail', params: { phenotypeId: entry['pk'] }}" >{{ entry['name'] }}</router-link>
                                                <p v-else-if="(key==='N studies' && currentView === 'Similar Phenotypes')">{{entry['studySet'].length}}</p>
                                                <p v-else>{{entry[key]}}</p>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </v-card>
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

    import {loadAssociationsOfPhenotype, loadPhenotype, loadSimilarPhenotypes, loadStudy} from "../api";
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
      tabNames = {"List of Studies": "listOfStudies", "Similar Phenotypes": "similarPhenotypes"};
      tabData = {listOfStudies: [{}], similarPhenotypes: []};
      avgHitNumber = 0;
      phenotypeDescription: string = "";
      currentView: string = "Similar Phenotypes";
      araPhenoLink: string = "";
      columnsTab = {"Similar Phenotypes": ["name", "n studies", "description", "associated genes"], "List of Studies": ["study", "genotype", "method", "N hits"]};
      n = {phenotypes: 0, accessions: 0};
      filterKey: string = "";
      breadcrumbs = [{text: "Home", href: "/"}, {text: "Phenotypes", href: "/phenotypes"}, {text: this.phenotypeName, href: "", disabled: true}];

      maf = ["1", "1-5", "5-10", "10"];
      annotation = ["ns", "s", "in", "i"];
      type = ["genic", "non-genic"];
      chr = ["1", "2","3","4","5"];
      hideFields = ["phenotype"];
      showControls = ["chr","maf","annotation","type"];
      filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, type: this.type};
      phenotypeView = {name: "phenotype", phenotypeId: this.id, controlPosition: "right"};

//      TODO: add similar phenotypes fetching with Ontology

      get filteredStudiesAndPhenotypes() {
        let filterKey = this.filterKey;
        if (filterKey) {
          filterKey = filterKey.toLowerCase();
        }
        let data = this.tabData[this.tabNames[this.currentView]];
        if (filterKey) {
          data = data.filter((row) => {
            return Object.keys(row).some((key) => {
              return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
            });
          });
        }
        return data;
      }

      @Watch("id")
      onChangeId(val: number, oldVal: number) {
          this.loadData();
      }
      created(): void {
        this.loadData();
      }
      mounted(): void {
        this.currentView = "List of Studies";
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
        this.tabData.similarPhenotypes = data;
      }

      loadData(): void {
        try {
            loadPhenotype(this.id).then(this._displayPhenotypeData).then(this.loadStudyList);
            loadSimilarPhenotypes(this.id).then(this._displaySimilarPhenotypes);
        } catch (err) {
            console.log(err);

        }
      }
//    STUDIES FETCHING
      loadStudyList(data): void {
        for (const key of this.studyIDs) {
          loadStudy(key).then(this._addStudyData);
        }
        this.avgHitNumber = 0;
        for (let i = 0; i<this.tabData.listOfStudies.length; i++) {
            this.avgHitNumber += this.tabData.listOfStudies[i]["N hits"];
        }
        this.avgHitNumber = this.avgHitNumber / this.tabData.listOfStudies.length;
      }
      _addStudyData(data): void {
        if (Object.keys(this.studyIDs[0]).length === 0) {
          this.tabData.listOfStudies = [{
            "study": data.name,
            "genotype": data.genotype,
            "method": data.method,
            "transformation": data.transformation,
            "N hits": data.association_count, // TODO: Add proper number of hits in database
            "pk": data.pk,
          }];
        } else {
          this.tabData.listOfStudies = this.tabData.listOfStudies.concat([{
            "study": data.name,
            "genotype": data.genotype,
            "method": data.method,
            "transformation": data.transformation,
            "N hits": data.association_count,
            "pk": data.pk,
          }]);
        }
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
