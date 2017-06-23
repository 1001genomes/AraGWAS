<template>
    <div>
        <v-layout column align-start>
            <v-flex xs12>
                <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
            </v-flex>
        </v-layout>
        <v-tabs id="study-detail-tabs" grow scroll-bars v-model="currentView" class="mt-3">
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
                            <v-layout column>
                                <h5 class="mb-1">Distribution of significant associations</h5>
                                <v-tabs id="similar-tabs" grow scroll-bars v-model="currentViewIn">
                                    <v-tabs-bar slot="activators">
                                        <v-tabs-slider></v-tabs-slider>
                                        <v-tabs-item :href="'#' + i" ripple class="grey lighten-4 black--text"
                                                     v-for="i in ['On genes', 'On snp type']" :key="i">
                                            <div>{{ i }}</div>
                                        </v-tabs-item>
                                    </v-tabs-bar>
                                    <v-tabs-content :id="i" v-for="i in ['On genes', 'On snp type']" :key="i" class="pa-4">
                                        <div id="statistics" class="mt-2" v-if="sigAsDistributionRows[i].length > 0">
                                            <vue-chart :columns="sigAsDisributionColumns[i]" :rows="sigAsDistributionRows[i]" chart-type="PieChart"></vue-chart>
                                        </div>
                                        <h6 v-else style="text-align: center" >No significant hits.</h6>
                                    </v-tabs-content>
                                </v-tabs>
                            </v-layout>
                        </v-flex>
                    </v-flex>
                    <v-flex xs12 sm6 md8>
                        <h5 class="mb-1">Associations List</h5><v-divider></v-divider>
                        <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields" :view="phenotypeView"></top-associations>
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
                        <manhattan-plot class="flex" :dataPoints="dataChr[i.toString()]" v-for="i in [1, 2, 3, 4, 5]" :options="options[i.toString()]"></manhattan-plot>
                    </v-flex>
                </v-layout>
            </v-tabs-content>
        </v-tabs>
    </div>
</template>

<script lang="ts">
    import Vue from "vue";

    import {Component, Prop, Watch} from "vue-property-decorator";

    import {loadAssociationsForManhattan, loadAssociationsOfStudy, loadPhenotype, loadStudy, loadStudyTopHits} from "../api";
    import ManhattanPlot from "../components/manhattanplot.vue";
    import Breadcrumbs from "./breadcrumbs.vue"
    import TopAssociationsComponent from "./topasso.vue"


    @Component({
      filters: {
        capitalize(str) {
            str = str.split("_").join(" ");
            return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          "manhattan-plot": ManhattanPlot,
          "breadcrumbs": Breadcrumbs,
          "top-associations": TopAssociationsComponent,
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
      currentView: string = "study-detail-tabs-manhattan";
      currentViewIn: string = "On genes";
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
          "On genes": [["te", 0]],
          "On snp type": [["string", 0]]};

      breadcrumbs = [{text: "Home", href: "/"}, {text: "Studies", href: "/studies"}, {text: this.studyName, href: "", disabled: true}];

      maf = ["1", "1-5", "5-10", "10"];
      annotation = ["ns", "s", "in", "i"];
      type = ["genic", "non-genic"];
      chr = ["1", "2","3","4","5"];
      hideFields = ["phenotype", "study"];
      showControls = ["chr","maf","annotation","type"];
      filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, type: this.type};
      phenotypeView = {name: "study", studyId: this.id, controlPosition: "right"};

      @Watch("id")
      onChangeId(val: number, oldVal: number) {
          this.loadData();
      }
      created(): void {
        this.loadData();
        this.currentView = "study-detail-tabs-details";
      }
      loadData(): void {
        try {
            loadStudy(this.id).then(this._displayStudyData);
            loadStudyTopHits(this.id).then(this._displayPieCharts);
            loadAssociationsForManhattan(this.id).then(this._displayManhattanPlots);
        } catch (err) {
            console.log(err);
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
        if (data.nHitsBonf) {
          this.bonferoniHits = data.nHitsBonf;
        }
        if (data.nHitsPerm) {
          this.permHits = data.nHitsPerm;
        }
        loadPhenotype(this.phenotypeId).then(this._loadAraPhenoLink);
      }
      _loadAraPhenoLink(data): void {
        this.araPhenoLink = data.araPhenoLink;
      }
      _displayPieCharts(data): void {
        this.sigAsDistributionRows['On genes'] = data.onGenes;
        this.sigAsDistributionRows['On snp type'] = data.onSnp;
        console.log('loadded')
      }
      _displayManhattanPlots(data): void {
        this.bonferoniThr01 = data.thresholds.bonferoniThreshold01;
        this.bonferoniThr05 = data.thresholds.bonferoniThreshold05;
        this.associationCount = data.thresholds.totalAssociations;
        for (let i=1; i <=5; i++) {
            let chrom = "chr" + i.toString();
            const positions = data[chrom].positions;
            const chrData: any[] = [];
            for (let j = 1; j < positions.length; j++) {
                const assoc = [positions[j],data[chrom].scores[j]];
                chrData.push(assoc);
            }
            this.dataChr[chrom] =  chrData;
            this.options[i.toString()]["bonferoniThreshold"] = data.bonferoniThreshold;
        }
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
