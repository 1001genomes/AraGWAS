<template>
    <div>
        <v-parallax src="/static/img/ara2.jpg" :height="height">
            <v-container>
                <v-layout column align-center justify-center v-if="!search">
                    <div class="banner-title">
                        <br>
                        <h1 class="white--text text-xs-center" >AraGWAS Catalog</h1>
                    </div>
                    <div class="banner-subtext">
                        <h5 class="white--text text-xs-center">The AraGWAS Catalog is a public and manually curated database for standardised GWAS results for <em>Arabidopsis thaliana</em>.</h5>
                        <br>
                        <h6 class="white--text light text-xs-center">This Database allows to search and filter for public GWASs, phenotypes and genes and to obtain additional meta-information. All GWASs were recomputed following a uniformed methodology to allow for comparable results.</h6>
                    </div>
                </v-layout>
            </v-container>
        </v-parallax>
        <v-container class="mt-3 pa-0">
            <v-card style="max-width: 800px;margin:0 auto;" class="search-container">
                <div class="pl-4 pt-1 pr-4">
                    <v-text-field
                            name="input-1"
                            label="Search the catalog (e.g. FLC, AT2G27035, chr2:1153551, flowering, PMC300268)"
                            v-model="searchQuery"
                            v-bind:focused="focused"
                            prepend-icon="search"
                    ></v-text-field>
                </div>
            </v-card>
        </v-container>
        <section v-if="!search">
            <v-container grid-list-md>
                <v-layout row wrap>
                    <v-flex xs12 >
                        <div class="icon-block">
                            <i class="icon material-icons">rowing</i>
                            <h5 >Take a tour</h5>
                            <p>Take a quick tour of AraGWAS to learn about the important functionalities.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1" id="tour-button" light @click="starttour">
                                <v-icon left dark>rowing</v-icon> Take a tour
                            </v-btn>
                        </div>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                        <div class="icon-block">
                            <i class="material-icons" >trending_up</i>
                            <h5>Top Associations</h5>
                            <p >Check out the top hits across the <em>Arabidopsis thaliana</em> genome.</p>
                            <v-btn dark class="btn--large green lighten-1 icon--left " id="top-assocations-button" light  to="/top-associations"><v-icon left dark>trending_up</v-icon>Top Associations</v-btn>
                        </div>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                        <div class="icon-block">
                                <i class="material-icons" >whatshot</i>
                                <h5 >Top Genes</h5>
                                <p >Check out the genes with most hits across the <em>Arabidopsis thaliana</em> genome.</p>
                                <v-btn dark class="btn--large green lighten-1 icon--left "   id="top-genes-button" light  to="/top-genes"><v-icon left dark>whatshot</v-icon>Top Genes</v-btn>
                            </div>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                         <div class="icon-block">
                            <i class="material-icons" >view_list</i>
                            <h5 >Public GWA Studies</h5>
                            <p >Browse through all available public <em>Arabidopsis thaliana</em> GWA studies.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1" id="studies-button" light  to="/studies"><v-icon left dark>view_list</v-icon> GWA Studies</v-btn>
                        </div>
                    </v-flex>
                    <v-flex xs12 sm6 md3>
                        <div class="icon-block">
                            <i class="material-icons" >grain</i>
                            <h5 >GWAS HitMap</h5>
                            <p >Check out the hitmap of hits across the <em>Arabidopsis thaliana</em> genome for all public GWA studies.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1" id="hitmap-button" light  to="/map"><v-icon left dark>grain</v-icon> GWAS HitMap</v-btn>
                        </div>
                    </v-flex>
                    <v-flex xs12 sm6 md6>
                        <div class="icon-block">
                            <i class="material-icons" >flash_off</i>
                            <h5 >Top KO Mutations</h5>
                            <p >Check out the highest-scoring KO mutations.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1" light  tag="a" to="/top-ko-mutations">
                                <v-icon left dark>flash_off</v-icon> Top KO Mutations
                            </v-btn>
                        </div>
                    </v-flex>
                    <v-flex xs12 sm6 md6>
                        <div class="icon-block">
                            <i class="material-icons" >grid_off</i>
                            <h5 >Top KO Genes</h5>
                            <p >Check out the genes with the largest number of associated KO mutations.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1" light  tag="a" to="/top-ko-genes">
                                <v-icon left dark>grid_off</v-icon> Top KO Genes
                            </v-btn>
                        </div>
                    </v-flex>
                    <v-flex xs12>
                        <div class="icon-block">
                            <i class="material-icons" >file_download</i>
                            <h5 >Download Center</h5>
                            <p >Download different files here.</p>
                            <v-btn dark class="btn--large icon--left green lighten-1" light id="download-center-button" tag="a" to="/download-center" v-tooltip:left="{html: 'Download Center for AraGWAS'}">
                                <v-icon left dark>file_download</v-icon> Download Center
                            </v-btn>
                        </div>
                    </v-flex>
                </v-layout>
            </v-container>
            <v-container grid-list-md>
                <v-layout row wrap>
                    <v-flex xs12 md4 order-md1 order-xs3 class="mt-5">
                        <h5 class="light black--text"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> News &amp; Updates</h5>
                        <v-card>
                            <v-card-text>
                                <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> AraGWAS Catalog paper published</div>
                                <div>
                                    <p class="light">
                                        We are happy to announce that the AraGWAS Catalog was published in the Database issue of Nucleic Acids Research:
                                    </p>
                                    <p class="light">
                                        Matteo Togninalli, Ümit Seren, Dazhe Meng, Joffrey Fitz, Magnus Nordborg, Detlef Weigel, Karsten Borgwardt, Arthur Korte, and Dominik G. Grimm; <b>The AraGWAS Catalog: a curated and standardized Arabidopsis thaliana GWAS catalog;</b> Nucleic Acids Research, gkx954, <a target=_blank href=https://doi.org/10.1093/nar/gkx954>https://doi.org/10.1093/nar/gkx954</a>
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                        <br>
                        <v-card>
                            <v-card-text>
                                <div style="font-size: 14pt"><v-icon class="green--text lighten-1 small-icon">fiber_new</v-icon> AraGWAS Catalog is online</div>
                                <div>
                                    <p class="light">
                                        We are proud to announce that the first public GWAS catalog for the model organism <em>Arabidopsis thaliana</em> has launched. We finalized a complete recomputation of Genome Wide Association Studies (GWAS) for 167 phenotypes with the brandly new imputed 2029 genomes from the 1001genomes consortium.
                                    </p>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-flex>
                    <v-flex xs12 sm6 md4 order-md3 class="mt-5">
                        <h5 class="black--text light"><v-icon class="green--text lighten-1 small-icon">assessment</v-icon> Quick Stats</h5>                      
                        <v-card>
                            <div class="title pa-4"><v-icon class="green--text lighten-1 small-icon">assignment</v-icon> {{ nStudies }} Studies</div><v-divider></v-divider>
                            <div class="title pa-4"><v-icon class="green--text lighten-1 small-icon">local_florist</v-icon> {{ nPhenotypes }} Phenotypes</div><v-divider ></v-divider>
                            <div class="title pa-4"><v-icon class="green--text lighten-1 small-icon">swap_calls</v-icon> {{ nAssociations }} Significant associations</div>
                        </v-card>

                        <h5 class="pt-4 black--text light"><v-icon class="green--text lighten-1 small-icon">data_usage</v-icon> Data</h5>
                            <vue-chart :columns="plotColumns" :rows="plotRows" :options="{pieHole: 0.2, title: 'Top genes by number of high-scoring associations'}" chart-type="PieChart"></vue-chart>
                    </v-flex>
                    <v-flex xs12 sm6 md4 order-md2 class="mt-5">
                        <h5 class=" black--text light"><v-icon class="green--text lighten-1 small-icon">insert_chart</v-icon> Twitter</h5>
                            <Timeline id="aragwas" sourceType="profile" :options="{ tweetLimit: '3' }"><div class="spinner"></div></Timeline>
                    </v-flex>
                </v-layout>
            </v-container>
        </section>

        <section v-if="search" class="container">
                <v-tabs id="search-result-tabs" grow icons dark v-model="currentView">
                    <v-tabs-bar>
                        <v-tabs-item :href="i" ripple class="green lighten-1"
                                v-for="i in ['studies','genes']" :key="i">
                            <section>
                                <div class="bold">Results: {{ i }}</div>
                                <div class="" v-if="n[i] === 1"><span class="arabadge">{{n[i]}} Result</span></div>
                                <div class="" v-else><span class="arabadge">{{n[i]}}<span v-if="i==='genes' & n[i]===200">+</span> Results</span></div>
                            </section>
                        </v-tabs-item>
                        <v-tabs-slider></v-tabs-slider>
                    </v-tabs-bar>
                    <v-tabs-items>
                        <v-tabs-content :id="i" v-for="i in ['studies','phenotypes','genes']" :key="i">
                            <v-card>
                                <v-card-text>
                                    <div id="results" class="col s12"><br>
                                        <h5 class="center" v-if="n[currentView] === 0">No {{observed[currentView]}} found for query: {{queryTerm}}</h5>
                                        <div v-else>
                                            <v-data-table  v-if=" currentView === 'studies' "
                                                        v-bind:headers="columnsStudies"
                                                        v-bind:items="dataObserved['studies']"
                                                        v-bind:pagination.sync="pagination"
                                                        hide-actions
                                                        :loading="loading"
                                                        :total-items="n['studies']"
                                                        class="elevation-0"
                                            >
                                                <template slot="headerCell" scope="props">
                                                    {{ props.header.text }}
                                                </template>
                                                <template slot="items" scope="props">
                                                    <td><router-link :to="{name: 'studyDetail', params: { id: props.item.pk }}">{{ props.item.phenotype }}</router-link></td>
                                                    <td  class="text-xs-left">{{ props.item.phenotypeToName }}</td>
                                                    <td  class="text-xs-left">{{ props.item.phenotypeDescription }}</td>
                                                    <td  class="text-xs-right">{{ props.item.nHitsPerm }}</td>
                                                    <!--<td  class="text-xs-left"><a :href="props.item.publication" target="_blank">{{ pub_names[props.item.publication] }}</a></td>-->
                                                    <td  class="text-xs-right">{{ props.item.genotype }}</td>
                                                </template>
                                            </v-data-table>
                                            <v-data-table  v-else
                                                        v-bind:headers="columnsGenes"
                                                        v-bind:items="dataObserved['genes']"
                                                        v-bind:pagination.sync="pagination"
                                                        hide-actions
                                                        :loading="loading"
                                                        :total-items="n['genes']"
                                                        class="elevation-0"
                                            >
                                                <template slot="headerCell" scope="props">
                                                    {{ props.header.text }}
                                                </template>
                                                <template slot="items" scope="props">
                                                    <td><router-link :to="{name: 'geneDetail', params: { geneId: props.item.name }}">{{ props.item.name }}</router-link></td>
                                                    <td  class="text-xs-right">{{ props.item.chr }}</td>
                                                    <td  class="text-xs-right">{{ props.item.start }}</td>
                                                    <td  class="text-xs-right">{{ props.item.end }}</td>
                                                    <td  class="text-xs-right">{{ props.item.strand }}</td>
                                                    <td  class="text-xs-left">{{ props.item.description }}</td>
                                                </template>
                                            </v-data-table>
                                        </div>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-tabs-content>
                    </v-tabs-items>
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
    import { Timeline, Tweet } from 'vue-tweet-embed';

    import {search, loadPhenotypes, loadStudies, loadAssociationCount, loadTopGenes} from '../api';
    import LineChart from "../components/linechart.vue";
    import Router from "../router";
    import _ from 'lodash';

    import tourMixin from "../mixins/tour.js";

    Component.registerHooks(['beforeRouteLeave']);
    @Component({
      filters: {
        capitalize(str) {
          return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          "line-chart": LineChart,
          "Timeline": Timeline,
      },
      mixins: [tourMixin]
    })
    export default class Home extends Vue {
      @Prop()
      queryTerm: string;
      @Prop()
      view: string;
      @Prop()
      page: number;
      currentView: string = "studies";
      currentPage: number = 1;
      focused: boolean = false;
      searchQuery: string = "";
      columnsStudies = [{text: "Name", align: "left", value: "name",},{text: "Phenotype Ontology",align: "left", value: "phenotypeToName",sortable:false},{text: "Phenotype Description",align: "left", value: "phenotypeDescription", sortable: false,},{text:  "N Hits Permutation", value: "nHitsPerm"},{text:  "Genotype", value: "genotype"}]; //,{text: "Publication",align: "left", value: "publication", sortable: false}
//      columnsStudies = ["name", "transformation", "method", "genotype", "n Hits Permutation","phenotype Description"];
      pagination = {rowsPerPage: 25, totalItems: 0, page: 1, sortBy: "nHitsPerm", descending: true};
      loading: boolean = true;

//      columnsPhenotypes = ["name", "description"];
      columnsGenes = [{text: "Name", align: "left", value: "name",sortable: false},{text:"Chr", value:"chr",sortable: false},{text:"Start position", value:"start",sortable: false},{text:"End position", value:"end",sortable: false}, {text: "Strand", value: "strand",sortable: false},{text:"Description",value:"description",align:"left",sortable: false}];
//      columnsGenes = ["name", "chr", "start position", "end position", "strand", "description"];
      dataObserved = {studies: [], phenotypes: [], genes: []};
      observed = {studies: "Study", phenotypes: "Phenotype", genes: "Gene"};
      n = {studies: 0, phenotypes: 0, genes: 0};
      pageCount = {studies: 5, phenotypes: 5, genes: 5};
      nStudies = 0;
      nPhenotypes = 0;
      nAssociations = 0;
      plotRows = [["Gene 1",11],["Gene 2",2],["Gene 3",2],["Gene 4",2],["Sleep",7]];
      plotColumns = [{"type": "string", "label": "Condition"},{"type": "number","label":"#Count"}];
      pub_names = {'https://doi.org/10.1038/nature08800':'Atwell et. al, Nature 2010', 'https://doi.org/10.1073/pnas.1007431107':'Flowering time in simulated seasons', 'https://doi.org/10.1038/ng.2824':'Mejion', 'https://doi.org/10.1073/pnas.1503272112':'DAAR', 'https://doi.org/10.1371/journal.pbio.1002009':'Ion Concentration','https://doi.org/10.1016/j.cell.2016.05.063':'1001genomes flowering time phenotypes'};

      debouncedUpdateUrl = _.debounce(this.updateUrl, 300);

      tourOptions = {
        steps : [
        {
          element: ".parallax",
          intro: "AraGWAS Catalog is a public database collection of <em>Arabidopsis thaliana</em> GWA studies. This tour will show the important features",
          position: "bottom-middle-aligned"
        },
        {
          element: ".search-container",
          intro: "The global search form allows the user to search across all phenotypes, studies and genomic regions"
        },
        {
          element: "#download-center-button",
          intro: "You can find several download options in the download center"
        },
        {
          element: "#studies-button",
          intro: "You can access the list of available GWA studies by clicking here"
        },
        {
          element: "#top-genes-button",
          intro: "To see the the genes with most associations, press here"
        },
        {
          element: "#hitmap-button",
          intro: "The GWAS Hitmap provides a 10.000 foot view on all significant associations across all phenotypes. It allows the user to easily spot pleiotropic effects of certain genomic regions"
        },
        {
          element: "#top-assocations-button",
          intro: "To see the the top associations that are stored in the catalog, press here. To find out how to browse the top associations list, click on 'Next Page'"
        }
        ],
        nextPage: {name: "topAssociations"},

      };

      updateUrl() {
        if (this.searchQuery && this.searchQuery != "") {
            let page = this.currentPage ? this.currentPage.toString() : "1";
            let query = {queryTerm: this.searchQuery, view: this.currentView, page};
            this.$router.push({name: "home", query: query });
        }
        else  {
            this.$router.push({name: "home"});
        }
      }
      starttour(): void {
        this.$router.push({name:'home', query:{tour:'true'}})
      }

      @Watch("searchQuery")
      onSearchQueryChanged(val: string, oldVal: string) {
          if (val !== oldVal) {
            this.debouncedUpdateUrl();
          }
      }

      @Watch("pagination")
      onPaginationChanged(val: {}, oldVal: {}) {
        // only load when sorting is changed
        if (val["sortBy"] != oldVal["sortBy"] || val["descending"] != oldVal["descending"]) {
          this.loading = true;
          this.loadData(this.queryTerm, this.currentPage);
        }
      }

      @Watch("page")
      onPageChanged(val: number, oldVal: number) {
          this.currentPage = val;
          this.loadData(this.queryTerm, this.currentPage);
      }
      @Watch("view")
      onViewChanged(val: string, oldVal: string) {
          this.currentView = val;
      }

      @Watch("currentView")
      onCurrentViewChanged() {
          this.debouncedUpdateUrl();
      }

      @Watch("queryTerm")
      onQueryTermChanged(val: string, oldVal: string) {
        this.searchQuery = val;
        if (val != "") {
            this.loadData(val, this.currentPage);
        }
      }

      get search() {
          return (this.queryTerm && this.queryTerm != "");
      }

      get height() {
        if (this.search) {
            return 70;
        }
        return 340;
      }


      @Watch("currentPage")
      onCurrentPageChanged(val: number, oldVal: number) {
          if (val != oldVal) {
            this.debouncedUpdateUrl();
          }
      }
      created(): void {
        if (this.view && this.view != "") {
            this.currentView = this.view;
        }
        if (this.page) {
            this.currentPage = this.page;
        }
        if (this.queryTerm && this.queryTerm != "") {
            this.loadData(this.queryTerm, this.currentPage);
            this.searchQuery = this.queryTerm;
        }
        this.loadSummaryData();
      }
      loadData(queryTerm: string, page: number): void {
        const {sortBy, descending} = this.pagination;

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
        search(queryTerm, page, ordered).then(this._displayData);
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
                this.dataObserved.genes[gIdx]["start"] = this.dataObserved.genes[gIdx]["positions"]["gte"];
                this.dataObserved.genes[gIdx]["end"] = this.dataObserved.genes[gIdx]["positions"]["lte"];
                if (this.dataObserved.genes[gIdx]["aliases"].length > 0) {
                    this.dataObserved.genes[gIdx]["description"] = this.dataObserved.genes[gIdx].isoforms[0].shortDescription;
                }
            }
        }
        this.loading = false;
        this.chooseBestView()
      }
      chooseBestView(): void {
          if (this.n[this.currentView] == 0) {
              for (let view of ["studies","phenotypes","genes"]) {
                  if (this.n[view] > 0) {
                      this.currentView = view;
                      break
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
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
    .parallax__image-container:after {
        content: "\a ";
        width: 100%;
        height: 100%;
        top: 0px;
        left: 0px;
        background: rgba(0, 0, 0, 0.5);
        position: absolute;
        z-index: 1;
    }
</style>
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
        font-size: 2.8rem;

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

    .icon-block {
        text-align:center;
        display: flex;
        flex-direction: column;
        height: 100%;
        padding-top: 50px;
        align-items: center;
    }

    .icon-block > i.material-icons {
        font-size:2.2em;
        color: #4caf50 ;
    }
    .icon-block h5 {
        margin-bottom:5px;
        color: #4caf50 ;
    }

    .icon-block p {
        font-weight: 300;
        flex:1;
    }

    @media only screen and (min-width: 601px) {
        .banner-title h1 {
           font-size: 3.0rem;
        }
    }

    @media only screen and (min-width: 1024px) {
        .banner-title h1 {
           font-size: 4.2rem;
        }
    }
    /*ANIMATIONS*/

</style>
