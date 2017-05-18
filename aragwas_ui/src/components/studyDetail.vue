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
            <v-tabs
                    id="mobile-tabs-1"
                    grow
                    scroll-bars
                    :model="currentView"
                    style="border-color: transparent;"
            >
                <v-tab-item
                        v-for="i in ['Study details','Manhattan plots']" :key="i"
                        :href="'#' + i"
                        ripple
                        slot="activators"
                        class="grey lighten-4 black--text"
                        style="border-color: transparent;"
                >
                    <section style="width: 110%" @click="currentView = i">
                        <div v-if="currentView === i" class="black--text">{{ i }}</div>
                        <div v-else class="grey--text"> {{ i }}</div>
                    </section>
                </v-tab-item>
                <v-tab-content
                        v-for="i in ['Study details','Manhattan plots']" :key="i"
                        :id="i"
                        slot="content"
                        style="border-color: transparent;"
                >
                    <v-row v-if="currentView === 'Study details'">
                        <v-col xs5>
                                <br>
                                <v-col xs12>
                                    <div id="description">
                                        <v-row><v-col xs11><h5 class="mb-1">Description</h5><v-divider></v-divider></v-col></v-row>
                                        <div class="mt-4"></div>
                                        <v-row><v-col xs4><span>Name:</span></v-col><v-col xs7>{{ studyName }}</v-col></v-row>
                                        <v-row><v-col xs4><span>Phenotype:</span></v-col><v-col xs7> <router-link :to="{name: 'phenotypeDetail', params: { phenotypeId: phenotypeId }}">{{ phenotype }}</router-link></v-col></v-row>
                                        <v-row><v-col xs4><span>Genotype:</span></v-col><v-col xs7>{{ genotype }}</v-col></v-row>
                                        <v-row><v-col xs4><span>Transformation:</span></v-col><v-col xs7>{{ transformation }}</v-col></v-row>
                                        <v-row><v-col xs4><span>Method:</span></v-col><v-col xs7>{{ method }}</v-col></v-row>
                                        <v-row><v-col xs4><span>Publication:</span></v-col><v-col xs7><a v-bind:href=" publication">Link to publication</a></v-col></v-row>
                                        <v-row><v-col xs4><span>Total associations:</span></v-col><v-col xs7>{{ association_count }}</v-col></v-row>
                                        <!--TODO: Add n hits in database-->
                                        <v-row><v-col xs4><span>N hits (Bonferroni):</span></v-col><v-col xs7>{{  }}</v-col></v-row>
                                        <v-row><v-col xs4><span>N hits (with permutations):</span></v-col><v-col xs7>{{  }}</v-col></v-row>
                                        <v-row><v-col xs4><span>AraPheno link:</span></v-col><v-col xs7><a v-bind:href="arapheno_link" target="_blank">{{ phenotype }}</a></v-col></v-row>
                                        <v-row><v-col xs4><span>Accessions detail:</span></v-col><v-col xs7><a href="https://www.arabidopsis.org" target="_blank">arabidopsis.org</a></v-col></v-row>
                                        <div></div>
                                    </div>
                                    <v-row><v-col xs11><h5 class="mb-1 mt-4">Distribution of significant associations</h5><v-divider></v-divider></v-col></v-row>
                                    <v-tabs
                                            id="mobile-tabs-1"
                                            class="mt-2"
                                            grow
                                            scroll-bars
                                            :model="currentViewIn"
                                    >
                                        <v-tab-item
                                                v-for="i in ['On genes', 'On snp type']" :key="i"
                                                :href="'#' + i"
                                                ripple
                                                slot="activators"
                                                class="grey lighten-4 black--text tab-item"
                                        >
                                            <section style="width: 110%" @click="currentViewIn = i">
                                                <div v-if="currentViewIn === i" class="black--text">{{ i }}</div>
                                                <div v-else class="grey--text"> {{ i }}</div>
                                            </section>
                                        </v-tab-item>
                                        <v-tab-content
                                                v-for="i in ['On genes', 'On snp type']" :key="i"
                                                :id="i"
                                                slot="content"
                                        >
                                            <v-card>
                                                <div id="statistics" class="mt-2">
                                                    <vue-chart :columns="sig_as_distibution_columns[i]" :rows="sig_as_distibution_rows[i]" chart-type="PieChart"></vue-chart>
                                                </div>
                                            </v-card>
                                        </v-tab-content>
                                    </v-tabs>

                                </v-col>
                        </v-col>
                        <v-col xs7>
                            <br>
                            <v-row><v-col xs11><h5 class="mb-1">Associations List</h5><v-divider></v-divider></v-col></v-row>
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
                                                {{entry[key]}}
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
                    <v-row v-else>
                        <v-col xs12>
                            <br>
                            <v-col xs12>
                            <v-row><v-col xs11><h5 class="mb-1">Associations List</h5><v-divider></v-divider></v-col></v-row>
                            <manhattan-plot :dataPoints="dataChr2[i.toString()]" v-for="i in [1, 2, 3, 4, 5]" :options="{chr: i}"></manhattan-plot>
                            <vue-line-chart></vue-line-chart>
                            </v-col>
                        </v-col>
                    </v-row>
                </v-tab-content>
            </v-tabs>
        </v-container>
    </div>
</template>

<script lang="ts">
    import Vue from 'vue';
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import {loadStudy, loadAssociationsOfStudy, loadPhenotype} from '../api';
    import ManhattanPlot from '../components/manhattanplot.vue'

    @Component({
      filters: {
        capitalize(str) {
          return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          'manhattan-plot': ManhattanPlot,
      },
    })
    export default class StudyDetail extends Vue {
      @Prop()
      studyId: string = '';
      studyName: string = '';
      phenotype: string = '';
      phenotypeId: string = '';
      genotype: string = '';
      transformation: string;
      method: string;
      publication: string = '';
      association_count;
      arapheno_link: string = '';
      currentView: string = 'Study details';
      currentViewIn: string = 'On genes'
      columns = ['SNP', 'maf', 'p-value', 'beta', 'odds ratio', 'confidence interval', 'gene'];
      n = {phenotypes: 0, accessions: 0};

      dataChr2 = {
          '1': [[3021, 9], [3021, 5], [3000, 9], [1231, 2]],
          '2': [[8000, 9], [2131,4]]
      };

      sig_as_distibution_columns = {
          'On genes': [{'type': 'string', 'label': 'Condition'},{'type': 'number','label':'#Count'}],
          'On snp type': [{'type': 'string','label': 'Condition'},{'type': 'number','label':'#Count'}]};
      sig_as_distibution_rows = {
          'On genes': [['Gene 1',11],['Gene 2',2],['Gene 3',2],['Gene 4',2],['Sleep',7]],
          'On snp type': [['S',23],['SN', 2],['*', 2]]};

      sortOrders = {'snp': 1, 'maf': 1, 'pvalue': 1, 'beta': 1, 'odds ratio': 1, 'confidence interval': 1, 'gene': 1};
      sortKey: string = '';
      ordered: string = '';
      filterKey: string = '';
      associations = [];
      currentPage = 1;
      pageCount = 5;
      totalCount = 0;
      breadcrumbs = [{text: 'Home', href: '/'}, {text:'Studies', href: '#/studies'}, {text: this.studyName, href: '', disabled: true}];

      get filteredData () {
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

      @Watch('currentPage')
      onCurrentPageChanged(val: number, oldVal: number) {
        this.loadData(val);
      }
      created(): void {
        if (this.$route.params.studyId) {
          this.studyId = this.$route.params.studyId;
        }
        loadStudy(this.studyId).then(this._displayStudyData);
        this.loadData(this.currentPage);
      }
      loadData(page: number): void {
        loadAssociationsOfStudy(this.studyId, page, this.ordered).then(this._displayData);
      }
      _displayData(data): void {
        this.associations = data.results;
        this.currentPage = data.current_page;
        this.totalCount = data.count;
        this.pageCount = data.page_count;
      }
      _displayStudyData(data): void {
        this.studyName = data.name;
        this.genotype = data.genotype;
        this.transformation = data.transformation;
        this.method = data.method;
        this.phenotype = data.phenotype;
        this.publication = data.publication;
        this.phenotypeId = data.phenotype_pk;
        this.association_count = data.association_count;
        this.breadcrumbs[2].text = data.name;
        loadPhenotype(this.phenotypeId).then(this._loadAraPhenoLink);
      }
      _loadAraPhenoLink(data): void {
        this.arapheno_link = data.arapheno_link;
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
      // TODO: add association injection for manhattan plots
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
