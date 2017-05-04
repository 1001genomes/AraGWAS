<template>
    <div>
        <div class="banner-container" style="height: 80px">
            <div class="section" id="head">
                <div class="container">
                    <h4 class="white--text mt-3">
                        Study: {{ studyName }}
                    </h4>
                </div>
            </div>
            <v-parallax class="parallax-container" src="/static/img/ara1.jpg" height="80">
            </v-parallax>
        </div>
        <v-container>
            <v-row>
                <v-col xs6>
                        <br>
                        <v-col xs12>
                            <div id="description">
                                <h5>Description</h5>
                                <div></div>
                                <v-row><v-col xs3><span>Name:</span></v-col><v-col xs9>{{ studyName }}</v-col></v-row>
                                <v-row><v-col xs3><span>Phenotype:</span></v-col><v-col xs9> <router-link :to="{name: 'phenotypeDetail', params: { phenotypeId: phenotypeId }}">{{ phenotype }}</router-link></v-col></v-row>
                                <v-row><v-col xs3><span>AraPheno link:</span></v-col><v-col xs9><a href="https://arapheno.1001genomes.org/phenotype/31/">broken</a></v-col></v-row>
                                <v-row><v-col xs3><span>Genotype:</span></v-col><v-col xs9>{{ genotype }}</v-col></v-row>
                                <v-row><v-col xs3><span>Transformation:</span></v-col><v-col xs9>{{ transformation }}</v-col></v-row>
                                <v-row><v-col xs3><span>Method:</span></v-col><v-col xs9>{{ method }}</v-col></v-row>
                                <v-row><v-col xs3><span>easyGWAS link:</span></v-col><v-col xs9><a href="https://easygwas.ethz.ch/gwas/results/summary/a3c8b375-79d4-46f9-9341-8e9a244403bf/">GWAS-FT10</a></v-col></v-row>
                                <v-row><v-col xs3><span>Publication:</span></v-col><v-col xs9><a v-bind:href=" publication">Link to publication</a></v-col></v-row>
                                <div></div>
                            </div>
                            <div class="mt-3"><h5>Statistics</h5></div>
                            <div id="statistics">
                                <div>Accession origin:</div>
                                   <vue-chart :columns="[{'type': 'string','label': 'Year'},{'type': 'number','label':'#Count'}]" :rows="[['Work',11],['Eat',      2],['Commute',  2],['Watch TV', 2],['Sleep',    7]]" chart-type="PieChart"></vue-chart>
                                   <line-chart></line-chart>
                            </div>
                        </v-col>
                        <div id="to" class="col s12">
                            <div id="to_chart" class="chart"></div>
                        </div>
                        <div id="eo" class="col s12"><div class="chart" id="eo_chart"></div></div>
                        <div id="uo" class="col s12"><div class="chart" id="uo_chart"></div></div>
                </v-col>
                <v-col xs6>
                    <br>
                    <table>
                        <table>
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
                    </table>
                </v-col>
            </v-row>
            <v-row>
                <v-col xs12>
                    <h5>Manhattan Plots</h5>
                    <manhattan-plot></manhattan-plot>
                    <manhattan-plot></manhattan-plot>
                    <manhattan-plot></manhattan-plot>
                    <vue-line-chart></vue-line-chart>
                </v-col>
            </v-row>
        </v-container>
    </div>
</template>

<script lang="ts">
    import Vue from 'vue';
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import {loadStudy, loadAssociationsOfStudy} from '../api';
    import LineChart from '../components/linechart.vue';
    import ManhattanPlot from '../components/manhattanplot.vue'

    @Component({
      filters: {
        capitalize(str) {
          return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          'line-chart': LineChart,
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
      currentView: string = '';
      columns = ['SNP', 'maf', 'p-value', 'beta', 'odds ratio', 'confidence interval', 'gene'];
      n = {phenotypes: 0, accessions: 0};

      sortOrders = {'snp': 1, 'maf': 1, 'pvalue': 1, 'beta': 1, 'odds ratio': 1, 'confidence interval': 1, 'gene': 1};
      sortKey: string = '';
      ordered: string = '';
      filterKey: string = '';
      associations = [];
      currentPage = 1;
      pageCount = 5;
      totalCount = 0;
// TODO: add link to arapheno from loadPhenotype
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


    .parallax-container  {
        position:absolute;
        top:0;
        left:0;
        right:0;
        bottom:0;
        z-index:-1;
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
