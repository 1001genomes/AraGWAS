<template>
    <div>
        <v-layout row align-start>
            <v-flex xs6>
                <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
            </v-flex>
            <v-flex xs6 class="text-xs-right">
                <v-btn floating primary class="mr-3 mt-2" tag="a" :href="'/api/studies/'+id+'/download'" download v-tooltip:left="{html: 'Download whole HDF5 file'}">
                    <v-icon dark>file_download</v-icon>
                </v-btn>
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
                                    <v-flex xs5 md3>Original publication:</v-flex><v-flex xs7 mm9><a v-bind:href="publication">Link to original publication</a></v-flex>
                                    <v-flex xs5 md3>Number of samples:</v-flex><v-flex xs7 mm9>{{ samples }} <span v-if="countries">(from {{ countries }} different countries)</span></v-flex>
                                    <v-flex xs5 md3>Total associations:</v-flex><v-flex xs7 mm9>{{ associationCount }}</v-flex>
                                    <v-flex xs5 md3>Bonferroni threshold:</v-flex><v-flex xs7 mm9>{{ bonferroniThreshold }}</v-flex>
                                    <v-flex xs5 md3>Permutation threshold:</v-flex><v-flex xs7 mm9>{{ permutationThreshold }}</v-flex>
                                    <v-flex xs5 md3>N hits (Bonferroni):</v-flex><v-flex xs7 mm9>{{ bonferroniHits }}</v-flex>
                                    <v-flex xs5 md3>N hits (permutation):</v-flex><v-flex xs7 mm9>{{ permHits }}</v-flex>
                                    <!--<v-flex xs5 md3>N hits (with permutations):</v-flex><v-flex xs7 mm9>{{ permHits }}</v-flex>-->
                                </v-layout>
                            </v-layout>
                        </v-flex>
                        <v-flex xs12 class="mt-4">
                            <v-layout column>
                                <h5 class="mb-1">Distribution of significant associations</h5>
                                <study-plots :plotStatistics="plotStatistics"></study-plots>
                            </v-layout>
                        </v-flex>
                    </v-flex>
                    <v-flex xs12 sm6 md8>
                        <h5 class="mb-1">Associations List</h5><v-divider></v-divider>
                        <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields" :view="phenotypeView" @showAssociation></top-associations>
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
                        <manhattan-plot class="flex" :shown="(currentView==='study-detail-tabs-manhattan')" :dataPoints="dataChr['chr'+i.toString()]" v-for="i in [1, 2, 3, 4, 5]" :options="options[i.toString()]"></manhattan-plot>
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
    import ManhattanPlot from "./manhattanplot.vue";
    import Breadcrumbs from "./breadcrumbs.vue"
    import TopAssociationsComponent from "./topasso.vue"
    import StudyPlots from "./studyplots.vue"

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
          "study-plots": StudyPlots,
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
      bonferroniThr05: number = 0;
      bonferroniThr01: number = 0;
      bonferroniHits: number = 0;
      permHits: number = 0;
      fdrHits: number = 0;
      bonferroniThreshold: number = 0;
      permutationThreshold: number = 0;

      samples: number = 0;
      countries: number = 0;
      plotsWidth: number = 0;

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

      plotStatistics = {
          topGenes: {
              columns: [{type: "string", label: "Gene"}, {type: "number", label: "Count"}],
              rows: [["te", 0]],
          },
          genic: {
              columns: [{type: "string", label: "Condition"}, {type: "number", label: "Count"}],
              rows: [["te", 1]],
          },
          impact: {
              columns: [{type: "string", label: "Impact"}, {type: "number", label: "Count"}],
              rows: [["te", 1]],
          },
          annotation: {
              columns: [{type: "string", label: "Annotation"}, {type: "number", label: "Count"}],
              rows: [["te", 1]],
          },
          pvalueDistribution: {
              columns: [{type: "number", label: "pvalue range"}, {type: "number", label: "Count"}],
              rows: [[0, 1]],
          },
          mafDistribution: {
              columns: [{type: "string", label: "MAF range"}, {type: "number", label: "Count"}],
              rows: [['1', 0]],
          },
      };

      breadcrumbs = [{text: "Home", href: "/"}, {text: "Studies", href: "/studies"}, {text: this.studyName, href: "", disabled: true}];

      maf = ["1","1-5","5-10", "10"];
      mac = ["5"];
      annotation = ["ns", "s", "in", "i"];
      type = ["genic", "non-genic"];
      chr = ["1", "2","3","4","5"];
      hideFields = ["phenotype", "study"];
      showControls = ["chr","maf","annotation","type","mac", "significant"];
      filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, mac: this.mac, type: this.type, significant: "0"};
      phenotypeView = {name: "study", studyId: this.id, controlPosition: "right"};

      @Watch("id")
      onChangeId(val: number, oldVal: number) {
          this.loadData();
      }
      created(): void {
          this.loadData();
      }
      mounted(): void {
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
          this.bonferroniHits = data.nHitsBonf;
        }
        if (data.nHitsPerm) {
          this.permHits = data.nHitsPerm;
        }
        this.fdrHits = data.nHitsFdr;
        this.samples = data.numberSamples;
        this.countries = data.numberCountries;
        this.permutationThreshold = Number(Math.pow(10,-data.permutationThreshold).toPrecision(4));
        this.bonferroniThreshold = Number(Math.pow(10,-data.bonferroniThreshold).toPrecision(4));
        for (let i=1; i <=5; i++) {
            this.options[i.toString()]["permutationThreshold"] = data.permutationThreshold;
        }
        loadPhenotype(this.phenotypeId).then(this._loadAraPhenoLink);
      }
      _loadAraPhenoLink(data): void {
        this.araPhenoLink = data.araPhenoLink;
      }
      _displayPieCharts(data): void {
        this.plotStatistics.topGenes.rows = data.geneCount;
        this.plotStatistics.genic.rows = data.onSnpType;
        this.plotStatistics.impact.rows = data.impactCount;
        this.capitalize(this.plotStatistics.impact.rows);
        this.plotStatistics.annotation.rows = data.annotationCount;
        this.capitalize(this.plotStatistics.annotation.rows);
        this.plotStatistics.pvalueDistribution.rows = data.pvalueHist;
        this.plotStatistics.mafDistribution.rows = this.adjustHistogramsRows(data.mafHist);
        this.$emit('redrawChart');
      }
      capitalize(rows): void {
          // Helper function to transform ugly es strings into readable legends
          rows.forEach(function(part, index, theArray) {
              let str = theArray[index][0];
              str = str.split("_").join(" ");
              theArray[index][0] = str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
          });
      }
      adjustHistogramsRows(rows): Array<Array<string|number>> {
          rows.forEach(function(part, index, theArray){
              let str = theArray[index][0].toString()+'-'+(Math.round((theArray[index][0]+0.1)*10)/10).toString();
              theArray[index][0] = str;
          });
          return rows
      }
      _displayManhattanPlots(data): void {
        this.bonferroniThr01 = data.thresholds.bonferroniThreshold01;
        this.bonferroniThr05 = data.thresholds.bonferroniThreshold05;
        this.associationCount = data.thresholds.totalAssociations;
        for (let i=1; i <=5; i++) {
            let chrom = "chr" + i.toString();
            const positions = data[chrom].positions;
            const chrData: any[] = [];
            for (let j = 0; j < positions.length; j++) {
                const assoc = [positions[j],data[chrom].scores[j], data[chrom].mafs[j]];
                chrData.push(assoc);
            }
            this.dataChr[chrom] =  chrData;
            this.options[i.toString()]["bonferroniThreshold"] = data.thresholds.bonferroniThreshold05;
            this.options[i.toString()]["bonferroniThreshold"] = data.thresholds.bonferroniThreshold05;
            this.options[i.toString()]["max_y"] = Math.max(data[chrom].scores[0]+1, 10);
        }
      }
    }
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

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
