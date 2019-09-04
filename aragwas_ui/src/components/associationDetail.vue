<template>
    <div>
        <v-layout row align-start>
            <v-flex xs12>
                <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
            </v-flex>
            <v-flex xs3 class="text-xs-right">
                <v-btn floating primary small class="mr-3 mt-2" tag="a" :href="`api/associations/${this.id}_${this.assocId}/details.csv`" download v-tooltip:left="{html: 'Download table as csv'}">
                    <v-icon dark>file_download</v-icon>
                </v-btn>
            </v-flex>
        </v-layout>
        <v-layout row wrap class="pa-4 " >
            <v-flex xs12 md4 class="pa-1">
                <h5 class="mb-1">Association</h5>
                <v-divider></v-divider>
                <v-layout row wrap class="mt-4" id="snp_info_container">
                    <v-flex xs5 md4 >Chromosome:</v-flex><v-flex xs7 md8>{{ chr | capitalize }}</v-flex>
                    <v-flex xs5 md4 >Position:</v-flex><v-flex xs7 md8>{{ position }}</v-flex>
                    <v-flex xs5 md4 >Ref:</v-flex><v-flex xs7 md8>{{ ref }}</v-flex>
                    <v-flex xs5 md4 >Alt:</v-flex><v-flex xs7 md8>{{ alt }}</v-flex>
                    <v-flex xs5 md4>Gene:</v-flex><v-flex xs7 md8 >{{ gene }}</v-flex>
                    <v-flex xs5 md4>Annotation:</v-flex><v-flex xs8 mm8>{{ annotation }}</v-flex>
                    <v-flex xs5 md4>Score:</v-flex><v-flex xs7 md8 >{{ score }}</v-flex>
                    <v-flex xs5 md4>Significant:</v-flex><v-flex xs7 md8 >{{ overPermutation }}</v-flex>
                    <!--<v-flex xs5 md4>Type:</v-flex><v-flex xs7 mm8>{{ type }}</v-flex>-->
                    <v-flex xs12 md12>
                        <vue-chart :columns="pieColumns" :rows="pieRows" :options="{pieHole: 0.3, title: 'Allelic Distribution'}" chart-type="PieChart"></vue-chart>
                    </v-flex>
                </v-layout>
                <h5 class="mb-1">Study information</h5><v-divider></v-divider>
                <v-layout row wrap class="mt-4" id="association_info_container">
                    <v-flex xs5 md4>Genotype:</v-flex><v-flex xs7 mm8>{{ genotype }}</v-flex>
                    <v-flex xs5 md4>Transformation:</v-flex><v-flex xs7 mm8>{{ transformation }}</v-flex>
                    <v-flex xs5 md4>Method:</v-flex><v-flex xs7 mm8>{{ method }}</v-flex>
                    <v-flex xs5 md4>Number of samples:</v-flex><v-flex xs7 mm8>{{ samples }} <span v-if="countries">(from {{ countries }} different countries)</span></v-flex>
                    <v-flex xs5 md4>Total associations:</v-flex><v-flex xs7 mm8>{{ associationCount }}</v-flex>
                    <v-flex xs5 md4>Bonferroni threshold:</v-flex><v-flex xs7 mm8>{{ bonferroniThreshold }}</v-flex>
                    <v-flex xs5 md4>Permutation threshold:</v-flex><v-flex xs7 mm8>{{ permutationThreshold }}</v-flex>
                    <v-flex xs5 md4>N hits (Bonferroni):</v-flex><v-flex xs7 mm8>{{ bonferroniHits }}</v-flex>
                    <v-flex xs5 md4>N hits (permutation):</v-flex><v-flex xs7 mm8>{{ permHits }}</v-flex>
                </v-layout>
            </v-flex>
            <v-flex xs12 md8>
                <v-tabs id="assocation-detail-tabs" class="fill-height" grow scroll-bars v-model="currentView" >
                    <v-tabs-bar>
                        <v-tabs-slider></v-tabs-slider>
                        <v-tabs-item href="#association-detail-tabs-table" ripple class="grey lighten-4 black--text">
                            <div>Accession Table</div>
                        </v-tabs-item>
                        <v-tabs-item href="#association-detail-tabs-explorer" ripple class="grey lighten-4 black--text" >
                            <div id = "explorer_tab">Phenotype explorer</div>
                        </v-tabs-item>
                        <v-tabs-item href="#association-detail-tabs-plots" ripple class="grey lighten-4 black--text" >
                            <div id = "plot_tab">Candlestick charts</div>
                        </v-tabs-item>
                    </v-tabs-bar>
                    <v-tabs-items class="fill-height">
                        <v-tabs-content id="association-detail-tabs-table" class="pa-4 " >
                            <v-layout >
                                <v-flex wrap fill-height class="pl-1 pr-1 associations-table-container" >
                                    <v-data-table
                                        :headers="headers"
                                        :items="accessionTable"
                                        :pagination.sync="pagination"
                                        hide-details
                                        :loading="loading"
                                        class="elevation-1 mt-2 asso-table"
                                    >
                                    <template slot="headerCell" scope="props">
                                        <span v-tooltip:bottom="{ 'html': props.header.tooltip}">
                                        {{ props.header.text | capitalize }}
                                        </span>
                                    </template>
                                    <template slot="items" scope="props">
                                        <tr :id="props.item.obsUnitId">
                                            <td>
                                                {{ props.item.accessionId }}
                                            </td>
                                            <td class="text-xs-right">{{ props.item.accessionName }}</td>
                                            <td class="text-xs-right">
                                                <span>
                                                    <div class="phenotpe-bar" :style="{width: ((props.item.phenotypeValue - phenotypeMinValue)/( phenotypeMaxValue - phenotypeMinValue))* 100 + '%'}"></div>
                                                </span>
                                                <span> {{ props.item.phenotypeValue }} </span>

                                            </td>
                                            <td class="text-xs-right">{{ props.item.accessionLongitude }}</td>
                                            <td class="text-xs-right">{{ props.item.accessionLatitude }}</td>
                                            <td class="text-xs-right">{{ props.item.accessionCountry }}</td>
                                            <td class="text-xs-right">{{ props.item.allele }}</td>
                                        </tr>
                                    </template>
                                </v-data-table>
                                </v-flex>
                            </v-layout>
                        </v-tabs-content>
                        <v-tabs-content id="association-detail-tabs-explorer"   class="pa-4 fill-height" >
                            <v-flex wrap fill-height class="pl-1 pr-1"  >
                                <vue-chart ref="motionChart" v-if="motionRows!=null"  :columns="motionColumns" :rows="motionRows" :options="{width: width, height: height, state: state}" :packages="[{'packages': ['motionchart']}]" chart-type="MotionChart">
                                </vue-chart>
                                <div v-if="!hasFlash" class="flash_warning">
                                    <h5>
                                        This visualization requires Flash to be active/installed.<br>
                                        If you use Safari, try Firefox or Chrome
                                    </h5>
                                </div>
                            </v-flex>
                        </v-tabs-content>
                        <v-tabs-content id="association-detail-tabs-plots" class="pa-4" >
                            <v-layout row wrap class="pa-4 " >
                                <v-flex xs12 class="pa-1" id = "country_dropdown_container">
                                    <v-select
                                        :items="accessionCountries"
                                        v-model="selectedCountry"
                                        label="Select"
                                        single-line
                                        bottom
                                    ></v-select>
                                </v-flex>
                                <v-flex xs12 class="pa-1" >
                                    <distro-chart v-show="variationData != null" :data="variationData" ref="variatonPlots" ></distro-chart>
                                </v-flex>
                            </v-layout>
                        </v-tabs-content>
                    </v-tabs-items>
                </v-tabs>
            </v-flex>
        </v-layout>

    </div>
</template>

<script lang="ts">
    import Vue from "vue";

    import {Component, Prop, Watch} from "vue-property-decorator";
    import {loadStudy, loadPhenotype, loadAssociation, loadAssociationDetails} from "../api";
    import Breadcrumbs from "./breadcrumbs.vue";
    import Association from "../models/association";
    import Accession from "../models/accession";
    import DistroChart from "./distroChart.vue";
    import * as d3 from "d3";

    import _ from "lodash";

    import tourMixin from "../mixins/tour.js";

    @Component({
      filters: {
        capitalize(str) {
            str = str.split("_").join(" ");
            return str.charAt(0).toUpperCase() + str.slice(1);
        },
      },
      components: {
          "breadcrumbs": Breadcrumbs,
          "distro-chart": DistroChart,
      },
      mixins: [tourMixin],
    })
    export default class AssociationDetail extends Vue {
      @Prop({required: true})
      id: number;
      @Prop({required: true})
      assocId: string;

      // Assocation information
      chr: string = "";
      position: number = 0;
      score: number = 0;
      gene: string = "";
      ref: string = "";
      alt: string = "";
      maf: number = 0;
      annotation: string = "";
      overPermutation: boolean = false;
      overFDR: boolean = false;

      // Study information
      studyName: string = "";
      studyDOI: string = "";
      phenotype: string = "";
      phenotypeId: number = 0;
      genotype: string = "";
      transformation: string = "";
      method: string = "";
      publication: string = "";
      pubmedId: string = "";
      associationCount: number = 0 ;
      araPhenoLink: string = "";
      phenotypeDescription: string = "";
      phenotypeOntology: string = "";
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
      height: number = 0;
      width: number = 0;
      state: string = '{"dimensions":{"iconDimensions":["dim0"]},"xZoomedDataMin":0,"iconType":"VBAR","xZoomedIn":false,"time":"1988","yZoomedIn":false,"playDuration":15000,"xAxisOption":"5","iconKeySettings":[],"orderedByY":false,"yZoomedDataMax":70,"nonSelectedAlpha":0.4,"xLambda":1,"yZoomedDataMin":-40,"orderedByX":true,"xZoomedDataMax":389,"yAxisOption":"5","showTrails":false,"yLambda":1,"duration":{"multiplier":1,"timeUnit":"D"},"sizeOption":"_UNISIZE","uniColorForNonSelected":false,"colorOption":"6"}';

      debouncedOnResize = _.debounce(this.onResize, 300);
      phenotypeMinValue: number = 1;
      phenotypeMaxValue: number = 1;
      accessionTable: Accession[] = [];
      pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name, sortBy: "name", descending: true};
      currentPage = 1;
      hasFlash: boolean = false;
      variationData: any= null;

      loading: boolean = false;
      headers = [
          { text: "ID", value: "accessionId", name: "id", align: "left", tooltip: "ID of accession"},
          { text: "Name", value: "accessionName", name: "name", align: "right", tooltip: "Name of accession" },
          { text: "Phenotype", value: "phenotypeValue", name: "phenotype", align: "right", tooltip: "Phenotype"},
          { text: "Lon", value: "accessionLongitude", name: "longitude", align: "right", tooltip: "Longitude"},
          { text: "Lat", value: "accessionLatitude", name: "latitude", align: "right", tooltip: "Latitude"},
          { text: "Country", value: "accessionCountry", name: "country", align: "right", tooltip: "Country"},
          { text: "Allele", value: "allele", name: "allele", align: "right", tooltip: "Allele"},
      ];

      currentView: string = "association-detail-tabs-table";

      pieRows = [];
      pieColumns = [
          { type: "string", label: "Allele"},
          { type: "number", label: "#Count"},
        ];

      //motionRows = [];
      motionRows = null;

      motionColumns = [
        { type: "string", label: "Accession"},
        { type: "date", label: "Date"},
        { type: "string", label: "County"},
        { type: "number", label: "Phenotype"},
        { type: "number", label: "Longitude"},
        { type: "number", label: "Latitude"},
        { type: "string", label: "Allele"},
      ];


     selectedCountry: string = "";
     accessionCountries = [{value: "", text: "Worldwide"}];

      breadcrumbs = [{text: "Home", href: "/"},
      {text: "Associations", href: "/top-associations", disabled: false},
      {text: this.phenotype, href: "/study/" + this.id, disabled: false},
      {text: this.assocId, href: "" + this.id, disabled: true},
      ];

      tourOptions = {
        steps: [
            {
                element: "#snp_info_container",
                intro: "You find detailed information about the associated SNP here. The Pie chart shows the allelic distribution in the GWAS study.",
                position: "right",
            },
            {
                element: "#association_info_container",
                intro: "You find detailed information about the GWAS study here. You can see the number of significant associations, the method of the GWAS study and the genotype version.",
                position: "right",
            },
            {
                element: "#association-detail-tabs-table",
                intro: "The table contains all the accessions that where used in the GWAS study together with their phenotype value and allele for the corresponding SNP of the chosen association. The table can be sorted by phenotype or allele.",
                position: "left",
            },
            {
                element: "#explorer_tab",
                intro: "Switch to the motionchart.",
                position: "bottom",
            },
            {
                element: "#association-detail-tabs-explorer",
                intro: "The motionchart is a visual representation of the previous table. The axis can be sorted by latitude and longitude of the accessions and the bars/points can be colored by the allele. This can help the user to visually see geographic pattern in the allelel distrubtion. (Hint: You need to enable flash for this visualization)",
                position: "left",
            },
            {
                element: "#plot_tab",
                intro: "Switch to the candlestick charts.",
                position: "bottom",
            },
            {
                element: ".chart-wrapper",
                intro: "The candelstick charts show the effect of the two corresponding alleles on the phenotype distribution.",
                position: "left",
            },
            {
                element: ".chart-options",
                intro: "The user can select different visualizations other than a classic Box Plot. Additionally a trend line can be displayed.",
                position: "left",
            },
            {
                element: "#country_dropdown_container",
                intro: "By default the candlestick charts are display for all accessions in the GWAS study. The user can decide to display the candlestick charts for accessions from a certain country.",
                position: "left",
            },
            {
                element: ".faq",
                intro: "You will find more information and tutorials under the FAQ tab.",
                position: "bottom",
            },
            {
                element: "#rest-link",
                intro: "The REST documentation provides information about how to access the GWAS catalog programatically",
            },
            {
                element: ".aragwas-logo",
                intro: "This is the end of the tour. Enjoy AraGWAS Catalog!",
                position: "bottom",
            },
        ],
        callback: function(tour, component) {

            if (tour._currentStep < 3) {
                component.currentView = "association-detail-tabs-table";

            } else if (tour._currentStep == 3) {
                component.currentView = "association-detail-tabs-explorer";

            } else if (tour._currentStep == 5) {
                component.currentView = "association-detail-tabs-plots";
            }
            else if (tour._currentStep > 5) {
                component.onResize();
            }
        },

      };

      @Watch("id")
      onChangeId(val: number, oldVal: number) {
          this.loadData();
      }
      @Watch("currentView")
      onChangeTab(val: number, oldVal: number) {
          Vue.nextTick(() => {
              this.onResize();
          });
      }

      @Watch("selectedCountry")
      onChangeSelectedCountry(val: string, oldVal: string) {
           const variationData = [] as any;
           for (const accession of this.accessionTable) {
               if (val === "" || val === accession.accessionCountry) {
                variationData.push({ 'label': accession.allele, 'value': accession.phenotypeValue});
               }
           }
           this.variationData = variationData;
      }

      mounted(): void {
          this.onResize();
          this.loadData();
          window.addEventListener('resize', this.debouncedOnResize);
          this.hasFlash = ('undefined' != typeof navigator.mimeTypes['application/x-shockwave-flash']);
      }
      beforeDestroy() {
            window.removeEventListener('resize', this.debouncedOnResize);
     }

     onResize() {
         const chartComponent = this.$refs.motionChart as Vue;
         if (chartComponent == null)
            return;
         this.width = chartComponent.$el.offsetWidth;
         if (chartComponent.$el.parentElement != null) {
            this.height = chartComponent.$el.parentElement.offsetHeight;
        }
        if (this.currentView == "association-detail-tabs-plots") {
            const variatonPlots = this.$refs.variatonPlots as DistroChart;
            if (variatonPlots) {
                variatonPlots.onResize();
            }
        }
      }

      loadData(): void {
        try {
            this.loading = true;
            loadStudy(this.id).then(this._displayStudyData);
            const id: string = `${this.id}_${this.assocId}`;
            loadAssociation(id).then(this._displayAssociationData);
            loadAssociationDetails(id).then(this._displayAssocationDetails);
        } catch (err) {
            console.log(err);
        }
      }
      _displayAssociationData(data: Association): void {
          this.chr = data.snp.chr;
          this.score = data.score;
          this.position = data.snp.position;
          this.overPermutation = data.overPermutation;
          this.overFDR = data.overFDR;
          if (data.snp.annotations && data.snp.annotations.length > 0) {
            this.annotation = data.snp.annotations[0].effect;
          }
          this.ref = data.snp.ref;
          this.alt = data.snp.alt;
          this.score = this.score;
          this.gene = data.snp.geneName;
      }
      _displayAssocationDetails(data): void {
          this.accessionTable = data;
          const motionData = [] as any;
          const pieRows = [] as any;
          const accessionCountries = [] as any;
          const countryMap = {} as any;
          const alleleMap = {} as any;
          let minimumValue:number = Number.MAX_VALUE;
          let maximumValue:number = 0;
          const variationData = [] as any;
          for (const accession of this.accessionTable) {
              const row = [accession.accessionName, new Date (1988,0,1), accession.accessionCountry, accession.phenotypeValue, accession.accessionLongitude, accession.accessionLatitude, accession.allele];
              motionData.push(row);
              variationData.push({ 'label': accession.allele, 'value': accession.phenotypeValue});
              if (accession.allele in alleleMap) {
                  alleleMap[accession.allele] += 1;
              } else {
                  alleleMap[accession.allele] = 1;
              }
              if (accession.accessionCountry in countryMap) {
                  countryMap[accession.accessionCountry] += 1;
              } else {
                  countryMap[accession.accessionCountry] = 1;
              }
              if (minimumValue > accession.phenotypeValue) {
                  minimumValue = accession.phenotypeValue;
              }
              if (maximumValue < accession.phenotypeValue) {
                  maximumValue = accession.phenotypeValue;
              }
          }
          this.variationData = variationData;
          this.phenotypeMinValue = minimumValue;
          this.phenotypeMaxValue = maximumValue;
          for (const allele in alleleMap) {
              pieRows.push([allele, alleleMap[allele]]);
          }
          accessionCountries.push({'text': `Worldwide (${data.length})`, value: ""})
          for (const country in countryMap) {
              accessionCountries.push({text: `${country} ${countryMap[country]}`,value: country });
          }
          this.accessionCountries = accessionCountries;
          this.pieRows = pieRows;
          this.motionRows = motionData;
          this.loading = false;
          this.$emit('redrawChart');
      }

      _displayStudyData(data): void {
        this.studyName = data.name;
        this.genotype = data.genotype;
        this.transformation = data.transformation;
        this.method = data.method;
        this.phenotype = data.phenotype;
        this.publication = data.publication;
        this.pubmedId = data.publicationPmid;
        this.phenotypeId = data.phenotypePk;
        this.breadcrumbs[2].text = data.phenotype;
        this.studyDOI = data.doi;
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
        this.phenotypeOntology = data.phenotypeToName;
      }
      _displayPieCharts(data): void {
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
    }
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">

    @import "../stylus/main"

    h5 {
        color:$theme.primary;
    }

    .tabs__items
    {
        height:100%;
    }

    .flash_warning {
        display: flex;
        justify-content: center;
        height: 100%;
    }
    .flash_warning h5 {
        align-self: center;
        width: 60%;
        text-align: center;
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
    .phenotpe-bar {
        background-color: #058dc7;
        display: inline;
        float: left;
        height: 1.17em;
        margin: 0 10px 0 0;
        min-width: 1px;
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
