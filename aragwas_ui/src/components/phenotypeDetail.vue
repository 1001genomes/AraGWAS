<template>
    <div >
        <v-layout column align-start>
            <v-flex xs12>
                <v-breadcrumbs icons divider="chevron_right" class="left">
                    <v-breadcrumbs-item
                            v-for="item in breadcrumbs" :key="item"
                            :disabled="item.disabled"
                            class="breadcrumbsitem"
                            :href="{name: item.href}"
                            router
                    >
                        <span :class="['title', {'green--text': !item.disabled}]">{{ item.text}}</span>
                    </v-breadcrumbs-item>
                </v-breadcrumbs>
                <v-divider></v-divider>
            </v-flex>
        </v-layout>
        <v-layout row-sm wrap column class="mt-4">
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
                                                <router-link v-if="(key==='study' && currentView === 'List of Studies')" :to="{name: 'studyDetail', params: { studyId: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='name' && currentView === 'Similar Phenotypes')" :to="{name: 'phenotypeDetail', params: { phenotypeId: entry['pk'] }}" >{{ entry['name'] }}</router-link>
                                                <p v-else-if="(key==='N studies' && currentView === 'Similar Phenotypes')">{{entry['study_set'].length}}</p>
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
                <v-card class="mt-2">
                    <table class="table">
                        <thead>
                        <tr>
                            <th v-for="key in columns"
                                @click="sortBy(key)"
                                :class="{ active: sortKey == key }">
                                {{ key | capitalize }}
                                <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
                                    </span>
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="entry in filteredData">
                            <td v-for="key in columns">
                                <router-link v-if="(key==='gene')" :to="{name: 'geneDetail', params: { geneId: entry                ['gene']['pk'] }}" >{{entry[key]['name']}}</router-link>
                                <router-link v-else-if="(key==='study')" :to="{name: 'studyDetail', params: { geneId: entry['study']['pk'] }}" >{{entry[key]['name']}}</router-link>
                                <div v-else>{{entry[key]}}</div>
                            </td>
                        </tr>
                        </tbody>
                    </table>

                </v-card>
                <div class="page-container mt-5 mb-3">
                    <v-pagination :length.number="pageCount" v-model="currentPage" />
                </div>
            </v-flex>
        </v-layout>
    </div>
</template>

<script lang="ts">
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import {loadAssociationsOfPhenotype, loadPhenotype, loadSimilarPhenotypes, loadStudy} from "../api";

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
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
      columns = ["SNP", "pvalue", "gene", "study"];
      columnsTab = {"Similar Phenotypes": ["name", "n studies", "description", "associated genes"], "List of Studies": ["study", "genotype", "method", "N hits"]};
      n = {phenotypes: 0, accessions: 0};
      sortOrders = {snp: 1, pvalue: 1, gene: 1, study: 1};
      sortKey: string = "";
      ordered: string = "";
      filterKey: string = "";
      associations = [];
      currentPage = 1;
      pageCount = 5;
      totalCount = 0;
      breadcrumbs = [{text: "Home", href: "home"}, {text: "Phenotypes", href: "phenotypes"}, {text: this.phenotypeName, href: "", disabled: true}];

//      TODO: add similar phenotypes fetching with Ontology

      get filteredData() {
        let filterKey = this.filterKey;
        if (filterKey) {
          filterKey = filterKey.toLowerCase();
        }
        let data = this.associations;
        if (filterKey) {
          data = data.filter((row) => {
            return Object.keys(row).some((key) => {
              return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
            });
          });
        }
        return data;
      }
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

      @Watch("currentPage")
      onCurrentPageChanged(val: number, oldVal: number) {
        loadAssociationsOfPhenotype(this.id, val).then(this._displayData);
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
        this.araPhenoLink = data.araPhenoLink;
        this.breadcrumbs[2].text = data.name;
        this.studyNumber = data.study_set.length;
        this.studyIDs = data.study_set;
      }
      _displaySimilarPhenotypes(data): void {
        this.tabData.similarPhenotypes = data;
      }

//    ASSOCIATION LOADING

      loadData(): void {
        try {
            loadPhenotype(this.id).then(this._displayPhenotypeData).then(this.loadStudyList);
            loadSimilarPhenotypes(this.id).then(this._displaySimilarPhenotypes);
            loadAssociationsOfPhenotype(this.id, this.currentPage).then(this._displayData);
        } catch (err) {
            console.log(err);

        }
      }
      _displayData(data): void {
        this.associations = data.results;
        this.currentPage = data.current_page;
        this.totalCount = data.count;
        this.pageCount = data.page_count;
      }
//    STUDIES FETCHING
      loadStudyList(data): void {
        for (const key of this.studyIDs) {
          loadStudy(key).then(this._addStudyData);
        }
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

//    UTILITIES
      sortBy(key): void {
        this.sortKey = key;
        this.sortOrders[key] = this.sortOrders[key] * -1;
        if (this.sortOrders[key] < 0) {
          this.ordered = "-" + key;
        } else {
          this.ordered = key;
        }
        loadAssociationsOfPhenotype(this.id, this.currentPage).then(this._displayData);
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
