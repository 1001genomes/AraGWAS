<template>
    <div class="mt-0">
        <div class="banner-container" style="height: 80px">
            <div class="section">
                <div class="container">
                    <h4 class="white--text">
                        Search Results
                      </h4>
                </div>
            </div>
            <v-parallax class="parallax-container" src="/static/img/ara2.jpg" height="80">
            </v-parallax>
        </div>
        <div class="container">
            <v-tabs
                    id="mobile-tabs-1"
                    grow
                    scroll-bars
                    :model="currentView"
            >
                <v-tab-item
                        v-for="i in ['studies','phenotypes','associations']" :key="i"
                        :href="'#' + i"
                        ripple
                        slot="activators"
                        class="green lighten-1"
                >
                    <section style="width: 110%">
                        <div class="bold">Results: {{ i }}</div>
                        <div class="" v-if="n[i] === 1"><span class="arabadge">{{n[i]}} Result</span></div>
                        <div class="" v-else><span class="arabadge">{{n[i]}} Results</span></div>
                    </section>
                </v-tab-item>
                <v-tab-content
                        v-for="i in ['studies','phenotypes','associations']" :key="i"
                        :id="i"
                        slot="content"
                >
                    <v-card>
                        <v-card-text>
                            <div id="results" class="col s12"><br>
                                <h5 class="brown-text center" v-if="n[currentView] === 0">No {{observed[currentView]}} found for query: {{queryTerm}}</h5>
                                <table v-else>
                                    <thead>
                                    <tr>
                                        <th v-for="key in columns[currentView]"
                                            @click="sortBy(key)"
                                            :class="{ active: sortKey == key }">
                                            {{ key | capitalize }}
                                        <span class="arrow" :class="sortOrders[currentView][key] > 0 ? 'asc' : 'dsc' ">
                                        </span>
                                        </th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    <tr v-for="entry in filteredData">
                                        <td v-for="key in columns[currentView]">
                                            {{entry[key]}}
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-tab-content>
            </v-tabs>
            <div class="page-container mt-3 mb-3">
                <v-pagination v-bind:length.number="pageCount" v-model="currentPage"/>
            </div>
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from 'vue'
    import {Component, Watch, Prop} from 'vue-property-decorator'
//    import Study from '@/models/study'
//    import Page from '@/models/page'
    import {search} from '@/api'

    @Component({
      filters: {
        capitalize (str) {
          return str.charAt(0).toUpperCase() + str.slice(1)
        }
      }
    })
    export default class Results extends Vue {
      loading: boolean = false
//      resultsPage: Page<Study>
      sortOrdersStudies = {'name': 1, 'phenotype': 1, 'transformation': 1, 'method': 1, 'genotype': 1}
      columnsStudies = ['name', 'phenotype', 'transformation', 'method', 'genotype']
      sortOrdersPhenotypes = {'name': 1, 'description': 1}
      columnsPhenotypes = ['name', 'description']
      sortOrdersAssociations = {'snp': 1, 'maf': 1, 'pvalue': 1, 'beta': 1, 'odds_ratio': 1, 'confidence_interval': 1, 'phenotype': 1, 'study': 1}
      columnsAssociations = ['snp', 'maf', 'pvalue', 'beta', 'odds_ratio', 'confidence_interval', 'phenotype', 'study']
      columns = {'studies': this.columnsStudies, 'phenotypes': this.columnsPhenotypes, 'associations': this.columnsAssociations}
      sortOrders = {'studies': this.sortOrdersStudies, 'phenotypes': this.sortOrdersPhenotypes, 'associations': this.sortOrdersAssociations}
      sortKey: string = ''
      ordered: string = ''
      filterKey: string = ''
      currentPage = 1
      pageCount = 5
      @Prop
      queryTerm: string
      dataObserved = {'studies': [], 'phenotypes': [], 'associations': []}
      observed = {'studies': 'Study', 'phenotypes': 'Phenotype', 'associations': 'Association'}
      currentView: string = ''
      n = {'studies': 0, 'phenotypes': 0, 'associations': 0}

      get filteredData () {
        let filterKey = this.filterKey
        if (filterKey) {
          filterKey = filterKey.toLowerCase()
        }
        let data = this.dataObserved[this.currentView]
        if (filterKey) {
          data = data.filter(function (row) {
            return Object.keys(row).some(function (key) {
              return String(row[key]).toLowerCase().indexOf(filterKey) > -1
            })
          })
        }
        return data
      }

      @Watch('currentPage')
      onCurrentPageChanged (val:number, oldVal:number) {
        this.loadData(this.queryTerm, val)
      }
      created (): void {
        this.loadData(this.queryTerm, this.currentPage)
        this.currentView = 'studies'
      }
      loadData (queryTerm:string, page:number): void {
        search(queryTerm, page, this.ordered).then(this._displayData)
      }
      _displayData (data) : void {
        this.dataObserved['studies'] = data['results']['study_search_results']
        this.dataObserved['phenotypes'] = data['results']['phenotype_search_results']
        this.dataObserved['associations'] = data['results']['association_search_results']
        this.currentPage = data['current_page']
        this.pageCount = data['page_count']
        this.n['studies'] = data['count'][2]
        this.n['phenotypes'] = data['count'][1]
        this.n['associations'] = data['count'][0]
      }
      sortBy (key) : void {
        this.sortOrders[this.currentView][key] = this.sortOrders[this.currentView][key] * -1
        if (this.sortOrders[this.currentView][key] < 0) {
          this.ordered = '-' + key
        } else {
          this.ordered = key
        }
        this.sortKey = key
        this.loadData(this.queryTerm, this.currentPage)
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

    .parallax-container  {
        position:absolute;
        top:0;
        left:0;
        right:0;
        bottom:0;
        z-index:-1;
    }
    .col {
        width: 100%;
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

