<template>
<div class="mt-0">
  <div class="banner-container" style="height: 80px">
    <div class="section">
      <div class="container">
        <h4 class="white--text">
          Studies
        </h4>
      </div>
    </div>
   <v-parallax class="parallax-container" src="/static/img/ara2.jpg" height="80">
   </v-parallax>
  </div>
  <div class="container">
   <div class="section">
     <table class="table">
       <thead>
         <tr>
           <th v-for="key in columns"
           @click="sortBy(key)"
           :class="{ active: sortKey == key }"
           style="font-size: 11pt">
           {{ key | capitalize }}
           <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
           </span>
           </th>
         </tr>
       </thead>
       <tbody>
         <tr v-for="entry in filteredData">
           <td v-for="key in columns">
             <router-link v-if="(key==='name')" :to="{name: 'studyDetail', params: { studyId: entry['pk'] }}" >{{entry[key]}}</router-link>
             <router-link v-else-if="(key==='phenotype')" :to="{name: 'phenotypeDetail', params: { phenotypeId: entry['phenotype_pk'] }}" >{{entry[key]}}</router-link>
             <div v-else>{{entry[key]}}</div>
           </td>
         </tr>
       </tbody>
     </table>
   </div>
  </div>
  <div class="page-container mt-5 mb-3">
    <v-pagination :length.number="pageCount" v-model="currentPage" />
  </div>
</div>
</template>


<script lang="ts">
  import {Component, Watch} from 'vue-property-decorator';
  import {loadStudies} from '../api';
  import Page from '../models/page';
  import Study from '../models/study';
  import Vue from 'vue';

  @Component({
    filters: {
      capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
      },
    },
  })
  export default class Studies extends Vue {
    loading: boolean = false;
    studyPage: Page<Study>;
    sortOrders = {name: 1, phenotype: 1, transformation: 1, method: 1, genotype: 1};
    sortKey: string = '';
    ordered: string = '';
    columns: string[] = ['name', 'phenotype', 'transformation', 'method', 'genotype'];
    filterKey: string = '';
    studies = [];
    currentPage = 1;
    pageCount = 5;
    totalCount = 0;

    get filteredData() {
      let filterKey = this.filterKey;
      if (filterKey) {
        filterKey = filterKey.toLowerCase();
      }
      let data = this.studies;
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
      this.loadData(this.currentPage);
    }
    loadData(page: number): void {
      loadStudies(page, this.ordered).then(this._displayData);
    }
    _displayData(data): void {
      this.studies = data.results;
      this.currentPage = data.current_page;
      this.totalCount = data.count;
      this.pageCount = data.page_count;
    }
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
    .section {
        padding-top: 1rem;
    }
    .table {
      width: 100%;
      max-width: 100%;
      margin-bottom: 2rem;
    }
    .parallax-container  {
        position:absolute;
        top:0;
        left:0;
        right:0;
        bottom:0;
        z-index:-1;
    }
    .arrow {
      display: inline-block;
      vertical-align: middle;
      width: 0;
      height: 0;
      margin-left: 5px;
      opacity: 0;
    }

    .arrow.asc {
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-bottom: 4px solid green;
    }

    .arrow.dsc {
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 4px solid green;
    }

    th.active {
      color:black;
    }

    th.active .arrow {
      opacity: 1;
    }
    .page-container {
      display:flex;
      justify-content:center;

    }
</style>
