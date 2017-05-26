<template>
    <div>
        <div class="banner-container" style="height: 70px">
            <div class="section" id="head">
                <div class="container mt-3">
                    <v-breadcrumbs icons divider="chevron_right" class="left">
                        <v-breadcrumbs-item
                                v-for="item in breadcrumbs" :key="item"
                                :disabled="item.disabled"
                                class="breadcrumbsitem"
                                :href=" item.href "
                                target="_self"
                        >
                            <h5 v-if="item.disabled">{{ item.text }}</h5>
                            <h5 v-else class="green--text">{{ item.text }}</h5>
                        </v-breadcrumbs-item>
                    </v-breadcrumbs>
                    <v-divider></v-divider>
                </div>
            </div>
        </div>
        <v-container>
            <v-row>
                <v-col xs6>
                    <br>
                    <v-col xs12>
                        <div id="description" class="mb-5">
                            <v-row><v-col xs11><h5 class="mb-1">Description</h5><v-divider></v-divider></v-col></v-row>
                            <div class="mt-4"></div>
                            <v-row><v-col xs4><span>Name:</span></v-col><v-col xs7>{{ phenotypeName }}</v-col></v-row>
                            <v-row><v-col xs4><span>Number of studies:</span></v-col><v-col xs7>{{ studyNumber }}</v-col></v-row>
                            <v-row><v-col xs4><span>Average number of hits:</span></v-col><v-col xs7>{{ avgHitNumber }}</v-col></v-row>
                            <v-row><v-col xs4><span>AraPheno link:</span></v-col><v-col xs7><a v-bind:href=" arapheno_link " target="_blank">{{ phenotypeName }}</a></v-col></v-row>
                            <v-row><v-col xs4><span>Description:</span></v-col><v-col xs7>{{ phenotypeDescription }}</v-col></v-row>
                            <div></div>
                        </div>
                        <v-row class="mt-4"><v-col xs12>
                            <v-tabs
                                id="mobile-tabs-1"
                                grow
                                scroll-bars
                                :model="currentView"
                            >
                                <v-tab-item
                                        v-for="i in ['List of Studies', 'Similar Phenotypes']" :key="i"
                                        :href="'#' + i"
                                        ripple
                                        slot="activators"
                                        class="grey lighten-4 black--text"
                                >
                                    <section style="width: 110%" @click="currentView = i">
                                        <div v-if="currentView === i" class="black--text">{{ i }}</div>
                                        <div v-else class="grey--text"> {{ i }}</div>
                                    </section>
                                </v-tab-item>
                                <v-tab-content
                                        v-for="i in ['List of Studies','Similar Phenotypes']" :key="i"
                                        :id="i"
                                        slot="content"
                                >
                                    <v-card>
                                        <table class="table">
                                            <thead>
                                            <tr>
                                                <th v-for="key in columns_tab[i]"
                                                    @click="sortBy(key)"
                                                    :class="{ active: sortKey == key }">
                                                    {{ key | capitalize }}
                                                    <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
                                            </span>
                                                </th>
                                            </tr>
                                            </thead>
                                            <tbody>
                                            <tr v-if="currentView === 'List of Studies'" v-for="entry in filteredStudies">
                                                <td v-for="key in columns_tab[i]">
                                                    <router-link v-if="(key==='study' && currentView === 'List of Studies')" :to="{name: 'studyDetail', params: { studyId: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                    <p v-else>{{entry[key]}}</p>
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>
                                    </v-card>
                                </v-tab-content>
                        </v-tabs>
                        </v-col></v-row>
                    </v-col>
                </v-col>
                <v-col xs6>
                    <br>
                    <v-row><v-col xs12><h5 class="mb-1">Associations List</h5><v-divider></v-divider></v-col></v-row>
                    <v-col xs12>
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
                                        <router-link v-if="(key==='gene')" :to="{name: 'geneDetail', params: { geneId: entry['gene']['pk'] }}" >{{entry[key]['name']}}</router-link>
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
                    </v-col>
                </v-col>
            </v-row>
            <v-row>
                <v-col xs12>
                    <v-col xs12>

                    </v-col>


                </v-col>
            </v-row>
        </v-container>
    </div>
</template>

<script lang="ts">
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import Vue from 'vue';
    import {loadPhenotype, loadAssociationsOfPhenotype, loadStudy} from '../api';

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
    })
    export default class PhenotypeDetail extends Vue {
      @Prop()
      phenotypeId: string = '';
      phenotypeName: string = '';
      studyNumber = 0;
      studyIDs = [];
      studyData = [{}];
      avgHitNumber = 0;
      phenotypeDescription: string = '';
      currentView: string = 'List of Studies';
      arapheno_link: string = '';
      columns = ['SNP', 'pvalue', 'gene', 'study'];
      columns_tab = {'Similar Phenotypes': ['phenotype', 'n studies', 'average N hits', 'associated genes'], 'List of Studies': ['study', 'genotype', 'method', 'N hits']}
      n = {phenotypes: 0, accessions: 0};
      sortOrders = {snp: 1, pvalue: 1, gene: 1, study: 1};
      sortKey: string = '';
      ordered: string = '';
      filterKey: string = '';
      associations = [];
      currentPage = 1;
      pageCount = 5;
      totalCount = 0;
      breadcrumbs = [{text: 'Home', href: '/'}, {text:'Phenotypes', href: '#/phenotypes'}, {text: this.phenotypeName, href: '', disabled: true}];

//      TODO: Add computation of avg N hits
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
      get filteredStudies() {
        let filterKey = this.filterKey;
        if (filterKey) {
          filterKey = filterKey.toLowerCase();
        }
        let data = this.studyData;
        if (filterKey) {
          data = data.filter((row) => {
            return Object.keys(row).some((key) => {
              return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
            });
          });
        }
        return data;
      }

      @Watch('currentPage')
      onCurrentPageChanged(val: number, oldVal: number) {
        this.loadData(val);
      }
      created(): void {
        if (this.$route.params.phenotypeId) {
          this.phenotypeId = this.$route.params.phenotypeId;
        }
        loadPhenotype(this.phenotypeId).then(this._displayPhenotypeData).then(this.loadStudyList);
        this.loadData(this.currentPage);
      }

//    PHENOTYPE DATA LOADING
      _displayPhenotypeData(data): void {
        this.phenotypeName = data.name;
        this.phenotypeDescription = data.description;
        this.arapheno_link = data.arapheno_link;
        this.breadcrumbs[2].text = data.name;
        this.studyNumber = data.study_set.length;
        this.studyIDs = data.study_set;
      }

//    ASSOCIATION LOADING
      loadData(page: number): void {
          // Load associations of all cited SNPs
       loadAssociationsOfPhenotype(this.phenotypeId, page, this.ordered).then(this._displayData)
      }
      _displayData(data): void {
        this.associations = data.results;
        this.currentPage = data.current_page;
        this.totalCount = data.count;
        this.pageCount = data.page_count;
      }
//    STUDIES FETCHING
      loadStudyList(data): void {
        for (let key of this.studyIDs) {
          loadStudy(key).then(this._addStudyData)
        }
      }
      _addStudyData(data): void {
        if(Object.keys(this.studyIDs[0]).length === 0){
          this.studyData = [{
            'study': data.name,
            'genotype': data.genotype,
            'method': data.method,
            'transformation': data.transformation,
            'N hits': data.association_count, // TODO: Add proper number of hits in database
            'pk': data.pk,
          }]
        }
        else{
          this.studyData = this.studyData.concat([{
            'study': data.name,
            'genotype': data.genotype,
            'method': data.method,
            'transformation': data.transformation,
            'N hits': data.association_count,
            'pk': data.pk,
          }])
        }
      }

//    UTILITIES
      sortBy(key): void {
        this.sortKey = key;
        this.sortOrders[key] = this.sortOrders[key] * -1;
        if (this.sortOrders[key] < 0) {
          this.ordered = '-' + key;
        } else {
          this.ordered = key;
        }
        this.loadData(this.currentPage);
      }
    }
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .banner-container {
        position: relative;
        overflow: hidden;
    }
    .breadcrumbsitem {
        font-size: 18pt;
    }

    .container {
        margin:0 auto;
        max-width: 1280px;
        width: 90%
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
        margin-bottom: 2rem;
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
