<template>
<div class="mt-0">
   <v-parallax src="/static/img/ara2.jpg" height="80">
   <div class="section">
      <div class="mb-2">
        <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
        </div>
    </div>
  </v-parallax>
  <div class="page-container">
   <div class="section">
     <v-data-table
             v-bind:headers="columns"
             v-bind:items="studies"
             v-bind:pagination.sync="pagination"
             hide-actions
             :loading="loading"
             :no-data-text="noDataText"
             :total-items="totalItems"
             class="elevation-1"
     >
       <template slot="headerCell" scope="props">
            {{ props.header.text }}
       </template>
       <template slot="items" scope="props">
         <td><router-link :to="{name: 'studyDetail', params: { id: props.item.pk }}">{{ props.item.phenotype }}</router-link></td>
         <!--<td><router-link :to="{name: 'phenotypeDetail', params: { id: props.item.phenotypePk }}">{{ props.item.phenotype }}</router-link></td>-->
         <td  class="text-xs-left">{{ props.item.phenotypeToName }}</td>
         <td  class="text-xs-left">{{ props.item.phenotypeDescription }}</td>
         <td  class="text-xs-right">{{ props.item.nHitsPerm }}</td>
         <!--<td  class="text-xs-left"><a :href="props.item.publication" target="_blank">{{ pub_names[props.item.publication] }}</a></td>-->
         <td  class="text-xs-right">{{ props.item.genotype }}</td>
       </template>
     </v-data-table>
   </div>
  </div>
  <div class="page-container mt-2 mb-3">
    <v-pagination :length.number="pageCount" v-model="currentPage" />
  </div>
</div>
</template>


<script lang="ts">
  import Vue from "vue";
  import {Component, Watch} from "vue-property-decorator";

  import {loadStudies} from "../api";
  import Page from "../models/page";
  import Study from "../models/study";
  import Breadcrumbs from './breadcrumbs.vue'

  @Component({
    filters: {
      capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
      },
    },
    components: {
      "breadcrumbs": Breadcrumbs,
    },
  })
  export default class Studies extends Vue {
    loading: boolean = false;
    noDataText: string = "No Data available.";
    studyPage: Page<Study>;
    columns = [{text: "Name", align: "left", value: "name",},{text: "Phenotype Ontology",align: "left", value: "phenotypeToName", sortable: false},{text: "Phenotype Description",align: "left", value: "phenotypeDescription", sortable: false},{text:  "N Hits Permutation", value: "nHitsPermutation",},{text:  "Genotype", value: "genotype",}]; // Removed/hidden: {text: "Phenotype", value: "phenotype"}, {text: "Publication",align: "left", value: "publication",},
    studies = [];
    pagination = {rowsPerPage: 25, totalItems: 0, page: 1, sortBy: "nHitsPermutation", descending: true};
    totalItems: number = 0;
    search: string = '';
    currentPage = 1;
    pageCount = 5;
    breadcrumbs = [{text: "Home", href: "/"}, {text: "Studies", href: "studies", disabled: true}];
    pub_names = {'https://doi.org/10.1038/nature08800':'Atwell et. al, Nature 2010', 'https://doi.org/10.1073/pnas.1007431107':'Flowering time in simulated seasons', 'https://doi.org/10.1038/ng.2824':'Mejion', 'https://doi.org/10.1073/pnas.1503272112':'DAAR', 'https://doi.org/10.1371/journal.pbio.1002009':'Ion Concentration','https://doi.org/10.1016/j.cell.2016.05.063':'1001genomes flowering time phenotypes'};


    @Watch("pagination")
    onPaginationChanged(val: {}, oldVal: {}) {
      // only load when sorting is changed
      if (val["sortBy"] != oldVal["sortBy"] || val["descending"] != oldVal["descending"]) {
        this.loading = true;
        this.noDataText = "Data is loading...";
        this.loadData(val, this.currentPage);
      }
    }
    @Watch("currentPage")
    onPaginationPageChanged(val: number, oldVal: number) {
      this.loading = true;
      this.noDataText = "Data is loading...";
      this.loadData(this.pagination, val);
    }
    created(): void {
      this.loading = true;
      this.noDataText = "Data is loading...";
      this.loadData(this.pagination, this.currentPage);
    }
    loadData(pagination, page: number): void {
      const {sortBy, descending} = pagination;

      let ordered = '';
      if (sortBy === null){
          ordered = '';
      } else {
        if (descending) {
          ordered = "-"+sortBy;
        } else {
          ordered = sortBy;
        }
      }
      loadStudies(page, ordered).then(this._displayData);
    }
    _displayData(data): void {
      this.studies = data.results;
      this.currentPage = data.currentPage;
      this.totalItems = data.count;
      this.pageCount = data.pageCount;
      this.loading = false;
      this.noDataText = "No Data available.";
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .section {
        width: 90%;
        padding-top: 1rem;
    }
    .page-container {
      display:flex;
      justify-content:center;
    }
</style>
