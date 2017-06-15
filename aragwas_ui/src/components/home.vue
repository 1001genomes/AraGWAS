<template>
    <div>
        <v-parallax src="/static/img/ara2.jpg" :height="height">
            <v-container>
                <v-layout column align-center justify-center v-if="!search">
                    <div class="banner-title">
                        <br>
                        <h1 class="white--text text-xs-center">Ara<b>GWAS</b>Catalog</h1>
                    </div>
                    <div class="banner-subtext">
                        <h5 class="white--text text-xs-center">Ara<b>GWAS</b>Catalog is a public database catalog of <em>Arabidopsis thaliana</em> associations from published GWASs.</h5>
                        <br>
                        <h6 class="white--text light text-xs-center">This Database allows to search and filter for public GWASs, phenotypes and genes and to obtain additional meta-information. All GWASs were recomputed following a uniformed methodology to allow for comparable results.</h6>
                    </div>
                </v-layout>
            </v-container>
        </v-parallax>
        <v-container class="mt-3 pa-0">
            <v-card style="max-width: 800px;margin:0 auto;">
                <div class="pl-4 pt-1 pr-4">
                    <v-text-field
                            name="input-1"
                            label="Search the catalog"
                            v-model="fastChange"
                            v-bind:focused="focused"
                            prepend-icon="search"
                            @input="debounceInput"
                    ></v-text-field>
                </div>
            </v-card>
        </v-container>
        <section v-if="!search">
            <div class="section">
                <v-container>
                    <v-layout class="text-xs-center">
                        <v-flex xs4 offset-xs2>
                            <div class="icon-block">
                                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">view_list</i></h3>
                                <h5 class="text-xs-center">Public GWAS Studies</h5>
                                <p class="light justify">Browse through all available public <em>Arabidopsis thaliana</em> GWAS studies.</p>
                                <v-btn class="btn--large icon--left green lighten-1" light router to="/studies"><v-icon left light>view_list</v-icon> GWAS Studies</v-btn>
                            </div>
                        </v-flex>
                        <v-flex xs4>
                            <div class="icon-block">
                                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">trending_up</i></h3>
                                <h5 class="text-xs-center">Top Associations</h5>
                                <p class="light justify">Check out the top hits for across the <em>Arabidopsis thaliana</em> genome.</p>
                                <v-btn class="btn--large green lighten-1 icon--left " light router to="/top-associations"><v-icon left light>trending_up</v-icon>Top Associations</v-btn>
                            </div>
                        </v-flex>
                    </v-layout>
                </v-container>
            </div>
            <v-container>
                <div class="section">
                    <v-layout>
                        <v-flex xs4 >
                            <h5 class="light black--text"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> News &amp; Updates</h5>
                            <v-card>
                                <v-card-text>
                                    <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> New Study Published</div>
                                    <div>
                                        <p class="light">
                                            We finalized a complete recomputation of 107 phenotypes GWAS with the brandly new imputed 3004 genomes from the 1001genomes consortium.
                                        </p>
                                    </div>
                                </v-card-text>
                            </v-card>
                            <br>
                            <v-card>
                                <v-card-text>
                                    <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> AraGWAS is online</div>
                                    <div>
                                        <p class="light">
                                            We are proud to announce that the first public GWAS catalogue for the model organism <em>Arabidopsis thaliana</em> has launched.
                                        </p>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-flex>
                        <v-flex xs8 >
                            <v-layout>
                                <v-flex xs6>
                                <h5 class="black--text light"><v-icon class="green--text lighten-1 small-icon">assessment</v-icon> Quick Stats</h5>
                                        <v-card>
                                            <div class="title pa-4"><v-icon class="green--text lighten-1 small-icon">assignment</v-icon> {{ nStudies }} Studies</div><v-divider></v-divider>
                                            <div class="title pa-4"><v-icon class="green--text lighten-1 small-icon">local_florist</v-icon> {{ nPhenotypes }} Phenotypes</div><v-divider ></v-divider>
                                            <div class="title pa-4"><v-icon class="green--text lighten-1 small-icon">swap_calls</v-icon> {{ nAssociations }} Associations</div>
                                        </v-card>
                                </v-flex>
                                <v-flex xs6>
                                    <h5 class=" black--text light"><v-icon class="green--text lighten-1 small-icon">data_usage</v-icon> Data</h5>
                                    <vue-chart :columns="plotColumns" :rows="plotRows" :options="{pieHole: 0.4, title: 'Top 8 genes by number of high-scoring associations'}" chart-type="PieChart"></vue-chart>
                                </v-flex>
                            </v-layout>
                        </v-flex>

                    </v-layout>
                </div>
            </v-container>
        </section>

        <section v-if="search" class="container">
                <v-tabs id="search-result-tabs" grow scroll-bars light v-model="currentView">
                    <v-tabs-bar slot="activators">
                        <v-tabs-slider></v-tabs-slider>
                        <v-tabs-item :href="i" ripple class="green lighten-1"
                                v-for="i in ['studies','phenotypes','genes']" :key="i">
                            <section>
                                <div class="bold">Results: {{ i }}</div>
                                <div class="" v-if="n[i] === 1"><span class="arabadge">{{n[i]}} Result</span></div>
                                <div class="" v-else><span class="arabadge">{{n[i]}}<span v-if="i==='genes' & n[i]===200">+</span> Results</span></div>
                            </section>
                        </v-tabs-item>
                    </v-tabs-bar>
                    <v-tabs-content :id="i" v-for="i in ['studies','phenotypes','genes']" :key="i">
                        <v-card>
                            <v-card-text>
                                <div id="results" class="col s12"><br>
                                    <h5 class="center" v-if="n[currentView] === 0">No {{observed[currentView]}} found for query: {{queryTerm}}</h5>
                                    <table v-else class="table">
                                        <thead>
                                        <tr>
                                            <th v-for="key in columns[currentView]"
                                                @click="sortBy(key)"
                                                :class="{ active: sortKey == key }"
                                                style="font-size:11pt">
                                                {{ key | capitalize }}
                                        <span class="arrow" :class="sortOrders[currentView][key] > 0 ? 'asc' : 'dsc' ">
                                        </span>
                                            </th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        <tr v-for="entry in filteredData">
                                            <td v-for="key in columns[currentView]">
                                                <router-link v-if="(key==='name' && currentView === 'studies')" :to="{name: 'studyDetail', params: { id: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='phenotype' && currentView === 'studies')" :to="{name: 'phenotypeDetail', params: { id: entry['phenotypePk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='name' && currentView==='phenotypes')" :to="{name: 'phenotypeDetail', params: { id: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='name' && currentView==='genes')" :to="{name: 'geneDetail', params: { geneId: entry[key] }}" >{{entry[key]}}</router-link>
                                                <div v-else>{{entry[key]}}</div>
                                            </td>
                                        </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-tabs-content>
                </v-tabs>
                <div class="page-container mt-3 mb-3">
                    <v-layout align-center justify-center >
                        <v-pagination v-bind:length.number="pageCount[currentView]" v-model="currentPage"/>
                    </v-layout>
                </div>
        </section>
    </div>
</template>

<script lang="ts">
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import {search, loadPhenotypes, loadStudies, loadAssociationCount, loadTopGenes} from '../api';
    import LineChart from "../components/linechart.vue";
    import Router from "../router";
    import debounce from '../../node_modules/debounce';

    Component.registerHooks(['beforeRouteLeave']);
    @Component({
      filters: {
        capitalize(str) {
          return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          "line-chart": LineChart,
      },
    })
    export default class Home extends Vue {
      @Prop()
      queryTerm: string;
      @Prop()
      currentView: string;
      @Prop()
      currentPage = 1;
      @Prop()
      focused: boolean;
      fastChange: string;
      router = Router;
      search: boolean = false;
      height = 280;
      sortOrdersStudies = {name: 1, phenotype: 1, transformation: 1, method: 1, genotype: 1};
      columnsStudies = ["name", "phenotype", "transformation", "method", "genotype"];
      sortOrdersPhenotypes = {name: 1, description: 1};
      columnsPhenotypes = ["name", "description"];
      sortOrdersGenes = {name: 1, chr: 1, start_pos: 1, end_pos: 1, strand: 1, description: 1};
      columnsGenes = ["name", "chr", "start position", "end position", "strand", "description"];
      columns = {studies: this.columnsStudies, phenotypes: this.columnsPhenotypes, genes: this.columnsGenes};
      sortOrders = {studies: this.sortOrdersStudies, phenotypes: this.sortOrdersPhenotypes, genes: this.sortOrdersGenes};
      sortKey: string = "";
      ordered: string = "";
      filterKey: string = "";
      dataObserved = {studies: [], phenotypes: [], genes: []};
      observed = {studies: "Study", phenotypes: "Phenotype", genes: "Gene"};
      n = {studies: 0, phenotypes: 0, genes: 0};
      pageCount = {studies: 5, phenotypes: 5, genes: 5};
      nStudies = 0;
      nPhenotypes = 0;
      nAssociations = 0;
      plotRows = [['Gene 1',11],['Gene 2',2],['Gene 3',2],['Gene 4',2],['Sleep',7]];
      plotColumns = [{'type': 'string', 'label': 'Condition'},{'type': 'number','label':'#Count'}];

      beforeRouteLeave (to, from, next) {
          if(to.path === '/studies' || to.path === '/top-associations'|| to.path === '/faq'){
              next()
          }
          else {
              window.history.replaceState({path: '/', params: {currentView: this.currentView, queryTerm: this.queryTerm, currentPage: this.currentPage}}, '', '#/results/'+this.currentView+"&"+this.queryTerm+"&"+this.currentPage)
              if(to.path === '/') {
                  this.currentView = '';
              }
              next();
          }

      }
//      beforeRouteUpdate (to, from, next) {
//          console.log('Update')
//          this.currentView = '';
//      }
      debounceInput() {
        debounce(this.updateQuery,  300, false)();
      }
      updateQuery() {
        this.queryTerm = this.fastChange;
      }
      @Watch("queryTerm")
      onQueryTermChanged(val: string, oldVal: string) {
        if (val === "") {
          this.search = false;
          this.height = 280;
        } else {
          this.search = true;
          this.height = 70;
          this.loadData(val, this.currentPage);
        }
      }
      loadResults() {
        this.router.push("/results/" + this.queryTerm);
      }
      moveTextUp() {
        this.search = false;
      }

      get filteredData () {
        let filterKey = this.filterKey;
        if (filterKey) {
          filterKey = filterKey.toLowerCase();
        }
        let data = this.dataObserved[this.currentView];
        if (filterKey) {
          data = data.filter((row) => {
            return Object.keys(row).some((key) => {
              return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
            });
          });
        }
        return data;
      }

      @Watch("currentPage")
      onCurrentPageChanged(val: number, oldVal: number) {
        this.loadData(this.queryTerm, val);
      }
      created(): void {
        this.currentView = "studies";
        if (this.$route.params.queryTerm && this.$route.params.queryTerm !== "") {
          this.queryTerm = this.$route.params.queryTerm;
          this.fastChange = this.queryTerm
          this.currentPage = +this.$route.params.currentPage;
          this.currentView = this.$route.params.currentView;
          this.search = true;
          this.height = 70;
        }
        this.loadData(this.queryTerm, this.currentPage);
        this.loadSummaryData();
      }
      loadData(queryTerm: string, page: number): void {
        search(queryTerm, page, this.ordered).then(this._displayData);
      }
      loadSummaryData(): void {
        loadStudies().then(this._countStudies);
        loadPhenotypes().then(this._countPhenotypes);
        loadAssociationCount().then(this._countAssociations);
        loadTopGenes().then(this._displayTopGenes)
      }

      _displayData(data): void {
        this.dataObserved.studies = data.results.studySearchResults;
        this.dataObserved.phenotypes = data.results.phenotypeSearchResults;
        this.dataObserved.genes = data.results.geneSearchResults;
        this.currentPage = data.currentPage;
        this.pageCount.studies = data.pageCount[2];
        this.pageCount.phenotypes = data.pageCount[1];
        this.pageCount.genes = data.pageCount[0];
        this.n.studies = data.count[2];
        this.n.phenotypes = data.count[1];
        this.n.genes = data.count[0];
        if (this.n.studies === 0) {
          this.dataObserved.studies = [];
        }
        if (this.n.phenotypes === 0) {
          this.dataObserved.phenotypes = [];
        }
        if (this.n.genes === 0) {
          this.dataObserved.genes = [];
        } else {
            for (const gIdx of Object.keys(this.dataObserved.genes)) {
                this.dataObserved.genes[gIdx]["start position"] = this.dataObserved.genes[gIdx]["positions"]["gte"];
                this.dataObserved.genes[gIdx]["end position"] = this.dataObserved.genes[gIdx]["positions"]["lte"];
                if (this.dataObserved.genes[gIdx]["aliases"].length > 0) {
                    this.dataObserved.genes[gIdx]["description"] = this.dataObserved.genes[gIdx]["aliases"][0]["full_name"];
                }
            }
        }
      }
      _displayTopGenes(data): void {
        this.plotRows = data;
      }

      _countStudies(data): void {
        this.nStudies = data.count;
      }
      _countPhenotypes(data): void {
        this.nPhenotypes = data.count;
      }
      _countAssociations(data): void {
        this.nAssociations = data;
      }
      sortBy(key): void {
        this.sortOrders[this.currentView][key] = this.sortOrders[this.currentView][key] * -1;
        if (this.sortOrders[this.currentView][key] < 0) {
          this.ordered = "-" + key;
        } else {
          this.ordered = key;
        }
        this.sortKey = key;
        this.loadData(this.queryTerm, this.currentPage);
      }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .parallax {
        margin-bottom:-24px;
    }

    .search-bar {
        position: relative;
        overflow: hidden;
        margin: 0 auto;
        max-width: 1280px;
        width: 90%
    }

    .small-icon {
        vertical-align: middle;
    }

    .table {
        width: 100%;
        max-width: 100%;
        margin-bottom: 2rem;
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

    .page-container {
        display:flex;
        justify-content:center;

    }
    .tabs__slider {
        background: #2e7d32;
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

    .table th {
        text-align:left;
    }
    th.active {
        color:black;
    }

    th.active .arrow {
        opacity: 1;
    }
    /*ANIMATIONS*/

</style>
