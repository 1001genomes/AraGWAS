<template>
    <div>
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
        <v-tabs id="study-detail-tabs" grow scroll-bars v:model="currentView" class="mt-3">
            <v-tabs-bar slot="activators">
                <v-tabs-slider></v-tabs-slider>
                <v-tabs-item href="#study-detail-tabs-details" ripple class="grey lighten-4 black--text">
                    <div>Study Details</div>
                </v-tabs-item>
                <v-tabs-item href="#study-detail-tabs-manhattan" ripple class="grey lighten-4 black--text" >
                    <div>Manhattan plots</div>
                </v-tabs-item>
                </v-tabs-bar>
            <v-tabs-content id="study-detail-tabs-details" class="pa-4" >
                <v-layout row-sm wrap column >
                    <v-flex xs12 sm6 md4>
                        <v-flex xs12 >
                            <v-layout column>
                                <h5 class="mb-1">Description</h5>
                                <v-divider></v-divider>
                                <v-layout row wrap class="mt-4">
                                    <v-flex xs5 md3 >Name:</v-flex><v-flex xs7 md9>{{ studyName }}</v-flex>
                                    <v-flex xs5 md3>Phenotype:</v-flex><v-flex xs7 md9 ><router-link :to="{name: 'phenotypeDetail', params: { id: phenotypeId }}">{{ phenotype }}</router-link></v-flex>
                                    <v-flex xs5 md3>Genotype:</v-flex><v-flex xs7 mm9>{{ genotype }}</v-flex>
                                    <v-flex xs5 md3>Transformation:</v-flex><v-flex xs7 mm9>{{ transformation }}</v-flex>
                                    <v-flex xs5 md3>Method:</v-flex><v-flex xs7 mm9>{{ method }}</v-flex>
                                    <v-flex xs5 md3>Original publication:</v-flex><v-flex xs7 mm9><a v-bind:href=" publication">Link to original publication</a></v-flex>

                                    <v-flex xs5 md3>Total associations:</v-flex><v-flex xs7 mm9>{{ associationCount }}</v-flex>
                                    <v-flex xs5 md3>N hits (Bonferoni):</v-flex><v-flex xs7 mm9>{{ bonferoniHits }}</v-flex>
                                    <v-flex xs5 md3>N hits (with permutations):</v-flex><v-flex xs7 mm9>{{ permHits }}</v-flex>
                                </v-layout>
                            </v-layout>
                        </v-flex>
                        <v-flex xs12 class="mt-4">
                            <h5 class="mb-1">Distribution of significant associations</h5>
                            <v-tabs id="similar-tabs" grow scroll-bars v:model="currentViewIn">
                                <v-tabs-bar slot="activators">
                                    <v-tabs-slider></v-tabs-slider>
                                    <v-tabs-item :href="'#' + i" ripple class="grey lighten-4 black--text"
                                            v-for="i in ['On genes', 'On snp type']" :key="i">
                                            <div>{{ i }}</div>
                                        </v-tabs-item>
                                </v-tabs-bar>
                                <v-tabs-content :id="i" v-for="i in ['On genes', 'On snp type']" :key="i" class="pa-4">
                                    <div id="statistics" class="mt-2" v-if=" (bonferoniHits>0) ">
                                        <vue-chart :columns="sigAsDisributionColumns[i]" :rows="sigAsDistributionRows[i]" chart-type="PieChart"></vue-chart>
                                    </div>
                                    <h6 v-else style="text-align: center" >No significant hits.</h6>
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
                                    <td class="regular" v-for="key in columns">
                                        <div v-if="(parseFloat(entry['pvalue']) > bonferoniThr05)">
                                            <router-link v-if="(key==='gene')" :to="{name: 'geneDetail', params: { geneId: entry['gene']['pk'] }}" >{{entry[key]['name']}}</router-link>
                                            <div v-else class="significant">{{entry[key]}}</div>
                                        </div>
                                        <div v-else>
                                            <router-link v-if="(key==='gene')" :to="{name: 'geneDetail', params: { geneId: entry['gene']['pk'] }}" >{{entry[key]['name']}}</router-link>
                                            <div v-else>{{entry[key]}}</div>
                                        </div>
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
            </v-tabs-content>
            <v-tabs-content id="study-detail-tabs-manhattan" class="pa-4" >
                <v-layout column child-flex>
                    <v-flex xs12>
                        <h5 class="mb-1">Manhattan Plots</h5>
                        <v-divider></v-divider>
                    </v-flex>
                    <v-flex xs12>
                        <manhattan-plot :dataPoints="dataChr[i.toString()]" v-for="i in [1, 2, 3, 4, 5]" :options="options[i.toString()]"></manhattan-plot>
                    </v-flex>
                </v-layout>
            </v-tabs-content>
        </v-tabs>
    </div>
</template>

<script lang="ts">
    import Vue from "vue";

    import {Component, Prop, Watch} from "vue-property-decorator";

    import {loadAssociationsForManhattan, loadAssociationsOfStudy, loadPhenotype, loadStudy} from "../api";
    import ManhattanPlot from "../components/manhattanplot.vue";

    @Component({
      filters: {
        capitalize(str) {
            str = str.split("_").join(" ");
            return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          "manhattan-plot": ManhattanPlot,
      },
    })
    export default class StudyDetail extends Vue {
      @Prop({required: true})
      id: number;
      studyName: string = "";
      phenotype: string = "";
      phenotypeId: number = 0;
      genotype: string = "";
      transformation: string = "";
      method: string = "";
      publication: string = "";
      associationCount: number = 0 ;
      araPhenoLink: string = "";
      currentView: string = "Study details";
      currentViewIn: string = "On genes";
      columns = ["SNP", "maf", "pvalue", "beta", "odds_ratio", "gene"]; // deleted confidence_interval for now
      n = {phenotypes: 0, accessions: 0};
      bonferoniThr05 = 0;
      bonferoniThr01 = 0;
      permThr = 0;
      bonferoniHits = 0;
      permHits = 0;

      // TODO: add permutation threshold retrieval from hdf5 files
      // TODO: add threshold choice
      // TODO: add hover description for Manhattan plots OR simple PNG loading from server

      dataChr = {
          1: [],
          2: [],
          3: [],
          4: [],
          5: [],
      };

      // Manhattan plots options
      options = {
          1: {chr: 1, max_x: 30427671},
          2: {chr: 2, max_x: 19698289},
          3: {chr: 3, max_x: 23459830},
          4: {chr: 4, max_x: 18585056},
          5: {chr: 5, max_x: 26975502},
      };

      sigAsDisributionColumns = {
          "On genes": [{type: "string", label: "Condition"}, {type: "number", label: "#Count"}],
          "On snp type": [{type: "string", label: "Condition"}, {type: "number", label: "#Count"}]};
      sigAsDistributionRows = {
          "On genes": [["te", "t"]],
          "On snp type": [["string", "number"]]};

      sortOrders = {snp: 1, maf: 1, pvalue: 1, beta: 1, odds_ratio: 1, confidence_interval: 1, gene: 1};
      sortKey: string = "";
      ordered: string = "";
      filterKey: string = "";
      associations = [];
      significantAssociations = [];
      currentPage = 1;
      pageCount = 5;
      totalCount = 0;
      breadcrumbs = [{text: "Home", href: "home"}, {text: "Studies", href: "studies"}, {text: this.studyName, href: "", disabled: true}];

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

      @Watch("id")
      onChangeId(val: number, oldVal: number) {
          this.loadData();
      }

      @Watch("currentPage")
      onCurrentPageChanged(val: number, oldVal: number) {
        loadAssociationsOfStudy(this.id, val).then(this._displayData);
      }
      created(): void {
        this.loadData();
      }
      loadData(): void {
        try {
            loadStudy(this.id).then(this._displayStudyData);
            loadAssociationsForManhattan(this.id).then(this._displayManhattanPlots);
            loadAssociationsOfStudy(this.id, this.currentPage).then(this._displayData);
        } catch (err) {
            console.log(err);
        }
      }
      _displayData(data): void {
        this.associations = data.results;
        this.currentPage = data.currentPage;
        this.totalCount = data.count;
        this.pageCount = data.pageCount;
        this.bonferoniThr01 = data.thresholds.bonferoniThreshold01;
        this.bonferoniThr05 = data.thresholds.bonferoniThreshold05;
        this.associationCount = data.thresholds.totalAssociations;
        for (const i in this.associations) {
          if (this.associations[i]["pvalue"] < this.bonferoniThr05) {
            this.significantAssociations[i] = this.associations[i];
            this.bonferoniHits = parseInt(i, 10);
            break;
          }
        }
        // Load pie data, get unique genes and SNP types
        for (const asso of this.significantAssociations) {
          let found = false;
          for (const gene of this.sigAsDistributionRows["On genes"]){
            if (asso["gene"]["name"].localeCompare(gene[0])) {
              gene[1] += 1;
              found = true;
              break;
            }
          }
          if (! found) {
            this.sigAsDistributionRows["On genes"].push([asso["gene"]["name"], 1]);
          }
          found = false;
          for (const type of this.sigAsDistributionRows["On snp type"]) {
            if (asso["type"].localeCompare(type[0])) {
              type[1] += 1;
              found = true;
              break;
            }
          }
          if (! found) {
            this.sigAsDistributionRows["On snp type"].push([asso["type"], 1]);
          }

        }

      }
      _displayStudyData(data): void {
        this.studyName = data.name;
        this.genotype = data.genotype;
        this.transformation = data.transformation;
        this.method = data.method;
        this.phenotype = data.phenotype;
        this.publication = data.publication;
        this.phenotypeId = data.phenotypePk;
        this.breadcrumbs[2].text = data.name;
        loadPhenotype(this.phenotypeId).then(this._loadAraPhenoLink);
      }
      _loadAraPhenoLink(data): void {
        this.araPhenoLink = data.araPhenoLink;
      }
      _displayManhattanPlots(data): void {
//        this.$nextTick(() => {
//            var manWidth = this.$refs.manhattan.clientWidth
//        });
        for (const i of [1, 2, 3, 4, 5]) {
            this.dataChr[i.toString()] = data["chr" + i.toString()].positions.map( (e, l) => [e, data["chr" + i.toString()].pvalues[l]]);
            this.options[i.toString()]["bonferoniThreshold"] = data.bonferoniThreshold;
//            this.options[i.toString()]["width"] = manWidth
        }
      }

      sortBy(key): void {
        this.sortKey = key;
        this.sortOrders[key] = this.sortOrders[key] * -1;
        if (this.sortOrders[key] < 0) {
          this.ordered = "-" + key;
        } else {
          this.ordered = key;
        }
        loadAssociationsOfStudy(this.id, this.currentPage).then(this._displayData);
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
    }
    .regular {
        font-weight: normal;
    }
    .significant {
        font-weight: bold;
    }

    ul.breadcrumbs {
        padding-left:0;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }
    .toolbar__item--active {
        color: #000;
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
