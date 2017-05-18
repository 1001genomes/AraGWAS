<template>
    <div>
        <div class="banner-container white--text" v-bind:style="{ height: height + 'px'}">
            <div class="container">
                <!--<transition name="custom-fadeOutUp" leave-active-class="animated fadeOutUp">-->
                    <div v-if="!search">
                    <div class="banner-title">
                        <br>
                        <h1 class="white--text text-xs-center">AraGWAS</h1>
                    </div>
                    <div class="banner-subtext">
                        <h5 class=" text-xs-center">AraGWAS is a public database catalog of <em>Arabidopsis thaliana</em> associations from published GWAS studies.</h5>
                        <br>
                        <h5 class="light text-xs-center">This Database allows to search and filter for public GWAS studies, phenotypes and genes and to obtain additional meta-information.</h5>
                    </div>
                    </div>
                <!--</transition>-->
                <br>
                <!--<transition name="bounce">-->
                    <v-text-field
                            name="input-1"
                            label="Search the catalog"
                            v-model="queryTerm"
                            v-bind:focused="focused"
                    ></v-text-field>
                <!--</transition>-->

            </div>
            <v-parallax class="parallax-container" src="/static/img/ara2.jpg" v-bind:height=" height ">
            </v-parallax>
        </div>
        <section v-if="!search">
            <div class="section mt-4">
                <div class="container">
                    <v-row class="text-xs-center">
                        <v-col xs12 md6 lg4>
                            <div class="icon-block">
                                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">view_list</i></h3>
                                <h5 class="text-xs-center">Public GWAS Studies</h5>
                                <p class="light justify">Browse through all available public <em>Arabidopsis thaliana</em> GWAS studies.</p>
                                <v-btn class="btn--large icon--left green lighten-1" router to="/studies"><v-icon left>view_list</v-icon> GWAS Studies</v-btn>
                            </div>
                        </v-col>
                        <v-col xs12 md6 lg4>
                            <div class="icon-block">
                                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">call_merge</i></h3>
                                <h5 class="text-xs-center">Meta-Analysis of Associations</h5>
                                <p class="light justify">Compare associations across phenotypes or for a specific gene region.</p>
                                <v-btn class="btn--large-focused icon--left green lighten-1" router to="/meta-analysis"><v-icon left>call_merge</v-icon> Meta-Analysis</v-btn>
                            </div>
                        </v-col>
                        <v-col xs12 md6 lg4>
                            <div class="icon-block">
                                <h3 class="text-xs-center green--text lighten-1"><i class="material-icons" style="font-size:35px">trending_up</i></h3>
                                <h5 class="text-xs-center">Top Associations</h5>
                                <p class="light justify">Check out the top hits for across the <em>Arabidopsis thaliana</em> genome.</p>
                                <v-btn class="btn--large green lighten-1 icon--left " router to="/top-association"><v-icon left>trending_up</v-icon>Top Associations</v-btn>
                            </div>
                        </v-col>
                    </v-row>
                </div>
            </div>
            <div class="container mt-5 mb-5">
                <div class="section">
                    <v-row>
                        <v-col xs4 >
                            <h5 class="light"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> News &amp; Updates</h5>
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
                        </v-col>
                        <v-col xs8 >
                            <v-row>
                                <v-col xs6>
                                <h5 class="light"><v-icon class="green--text lighten-1 small-icon">assessment</v-icon> Quick Stats</h5><v-divider class="mb-2"></v-divider>
                                        <v-card>
                                            <h6 class="pt-4 pl-4"><v-icon class="green--text lighten-1 small-icon">assignment</v-icon> {{ n_studies }} Studies</h6><v-divider class="mb-4"></v-divider>
                                            <h6 class="pl-4"><v-icon class="green--text lighten-1 small-icon">local_florist</v-icon> {{ n_phenotypes }} Phenotypes</h6><v-divider class="mb-4"></v-divider>
                                            <h6 class="pl-4 pb-4"><v-icon class="green--text lighten-1 small-icon">swap_calls</v-icon> {{ n_associations }} Associations</h6>
                                        </v-card>
                                </v-col>
                                <v-col xs6 >
                                    <h5 class="light"><v-icon class="green--text lighten-1 small-icon">data_usage</v-icon> Data</h5>
                                    <vue-chart :columns="[{'type': 'string', 'label': 'Condition'},{'type': 'number','label':'#Count'}]" :rows="[['Gene 1',11],['Gene 2',2],['Gene 3',2],['Gene 4',2],['Sleep',7]]" :options="{'pieHole': 0.4}" chart-type="PieChart"></vue-chart>
                                </v-col>
                            </v-row>
                            <v-row>
                                <v-col xs12 >
                                    <h5 class="light"><v-icon class="green--text lighten-1 small-icon">timeline</v-icon> New Studies</h5>
                                    <line-chart></line-chart>
                                </v-col>
                            </v-row>
                        </v-col>

                    </v-row>
                </div>
            </div>
        </section>
        <section v-if="search">
            <div class="container">
                <v-tabs
                        id="mobile-tabs-1"
                        grow
                        scroll-bars
                        :model="currentView"
                >
                    <v-tab-item
                            v-for="i in ['studies','phenotypes','genes']" :key="i"
                            :href="'#' + i"
                            ripple
                            slot="activators"
                            class="green lighten-1"
                    >
                        <section style="width: 110%" @click="currentView = i">
                            <div class="bold">Results: {{ i }}</div>
                            <div class="" v-if="n[i] === 1"><span class="arabadge">{{n[i]}} Result</span></div>
                            <div class="" v-else><span class="arabadge">{{n[i]}} Results</span></div>
                        </section>
                    </v-tab-item>
                    <v-tab-content
                            v-for="i in ['studies','phenotypes','genes']" :key="i"
                            :id="i"
                            slot="content"
                    >
                        <v-card>
                            <v-card-text>
                                <div id="results" class="col s12"><br>
                                    <h5 class="brown-text center" v-if="n[currentView] === 0">No {{observed[currentView]}} found for query: {{queryTerm}}</h5>
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
                                                <!--TODO: add links to studies views, need to be generated from study id-->
                                                <router-link v-if="(key==='name' && currentView === 'studies')" :to="{name: 'studyDetail', params: { studyId: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='phenotype' && currentView === 'studies')" :to="{name: 'phenotypeDetail', params: { phenotypeId: entry['phenotype_pk'] }}" >{{entry[key]}}</router-link>
                                                <router-link v-else-if="(key==='name' && currentView==='phenotypes')" :to="{name: 'phenotypeDetail', params: { phenotypeId: entry['pk'] }}" >{{entry[key]}}</router-link>
                                                <div v-else>{{entry[key]}}</div>
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
                        <v-pagination v-bind:length.number="pageCount[currentView]" v-model="currentPage"/>
                </div>
            </div>
        </section>
    </div>
</template>

<script lang="ts">
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import Router from '../router';
    import {search} from '../api';
    import LineChart from '../components/linechart.vue'
    import Vue from 'vue';

    @Component({
      filters: {
        capitalize(str) {
          return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          'line-chart': LineChart,
      }
    })
    export default class Althome extends Vue {
      @Prop()
      queryTerm: string;
      router = Router;
      search: boolean = false;
      height = 420;
      @Prop()
      focused: boolean;
      sortOrdersStudies = {name: 1, phenotype: 1, transformation: 1, method: 1, genotype: 1};
      columnsStudies = ['name', 'phenotype', 'transformation', 'method', 'genotype'];
      sortOrdersPhenotypes = {name: 1, description: 1};
      columnsPhenotypes = ['name', 'description'];
//      sortOrdersAssociations = {snp: 1, maf: 1, pvalue: 1, beta: 1, odds_ratio: 1, confidence_interval: 1, phenotype: 1, study: 1};
//      columnsAssociations = ['snp', 'maf', 'pvalue', 'beta', 'odds_ratio', 'confidence_interval', 'phenotype', 'study'];
      sortOrdersGenes = {name: 1, chr: 1, start_pos: 1, end_pos: 1, SNPs_count: 1, assicuations_count: 1, description: 1};
      columnsGenes = ['name', 'chr', 'start_pos', 'end_pos', 'SNPs_count', 'assicuations_count', 'description'];
      columns = {studies: this.columnsStudies, phenotypes: this.columnsPhenotypes, genes: this.columnsGenes};
      sortOrders = {studies: this.sortOrdersStudies, phenotypes: this.sortOrdersPhenotypes, genes: this.sortOrdersGenes};
      sortKey: string = '';
      ordered: string = '';
      filterKey: string = '';
      currentPage = 1;
      dataObserved = {studies: [], phenotypes: [], genes: []};
      observed = {studies: 'Study', phenotypes: 'Phenotype', genes: 'Gene'};
      currentView: string = '';
      n = {studies: 0, phenotypes: 0, genes: 0};
      pageCount = {studies: 5, phenotypes: 5, genes: 5};
      n_studies = 500;
      n_phenotypes = 200;
      n_associations = 1110000;

      @Watch('queryTerm') // TODO: add debounce for queries to api (https://vuejs.org/v2/guide/migration.html#debounce-Param-Attribute-for-v-model-removed)
      onQueryTermChanged(val: string, oldVal: string) {
        if (val === '') {
          this.search = false;
          this.height = 420;
        } else {
          this.search = true;
          this.height = 100;
          this.loadData(val, this.currentPage);
        }
      }
      loadResults() {
        this.router.push('/results/' + this.queryTerm);
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

      @Watch('currentPage')
      onCurrentPageChanged(val: number, oldVal: number) {
        this.loadData(this.queryTerm, val);
      }
      created(): void {
        this.loadData(this.queryTerm, this.currentPage);
        this.currentView = 'studies';
      }
      loadData(queryTerm: string, page: number): void {
        search(queryTerm, page, this.ordered).then(this._displayData);
      }
      _displayData(data): void {
        this.dataObserved.studies = data.results.study_search_results;
        this.dataObserved.phenotypes = data.results.phenotype_search_results;
        this.dataObserved.genes = data.results.gene_search_results;
        this.currentPage = data.current_page;
        this.pageCount.studies = data.page_count[2];
        this.pageCount.phenotypes = data.page_count[1];
        this.pageCount.genes = data.page_count[0];
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
        }
      }
      sortBy(key): void {
        this.sortOrders[this.currentView][key] = this.sortOrders[this.currentView][key] * -1;
        if (this.sortOrders[this.currentView][key] < 0) {
          this.ordered = '-' + key;
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
    .banner-container {
        position: relative;
        overflow: hidden;
    }


    .parallax-container  {
        position:absolute;
        top:0;
        left:0;
        right:0;
        bottom:0;
        z-index:-1;
    }

    .small-icon {
        vertical-align: middle;
    }

    .container {
        margin:0 auto;
        max-width: 1280px;
        width: 90%
    }

    .table {
        width: 100%;
        max-width: 100%;
        margin-bottom: 2rem;
    }

    .banner-title {

    }

    .banner-title h1 {
        font-size: 4.2rem;
        line-height: 110%;
        margin: 2.1rem 0 1.68rem 0;
    }

    .banner-subtext {

    }

    .banner-subtext h5 {
        font-weight:300;
        color:black;
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
    .page-container {
        display:flex;
        justify-content:center;

    }
    .tabs__slider {
        background: #f4d76c;
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
    /*ANIMATIONS*/

</style>
