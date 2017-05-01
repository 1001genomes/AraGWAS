<template>
    <div>
        <div class="banner-container" style="height: 80px">
            <div class="section" id="head">
                <div class="container">
                    <h4 class="white--text mt-3">
                        Phenotype: {{ phenotypeName }}
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
                            <v-row><v-col xs3><span>Name:</span></v-col><v-col xs9>{{ phenotypeName }}</v-col></v-row>
                            <v-row><v-col xs3><span>AraPheno link:</span></v-col><v-col xs9><a href="https://arapheno.1001genomes.org/phenotype/31/">FT10</a></v-col></v-row>
                            <v-row><v-col xs3><span>Genotype:</span></v-col><v-col xs9>{{ genotype }}</v-col></v-row>
                            <v-row><v-col xs3><span>Transformation:</span></v-col><v-col xs9>{{ transformation }}</v-col></v-row>
                            <v-row><v-col xs3><span>Scoring:</span></v-col><v-col xs9>{{ scoring }}</v-col></v-row>
                            <div></div>
                        </div>
                        <div class="mt-3"><h5>Similar phenotypes</h5></div>
                        <div id="statistics">
                            <v-card>
                                <v-list two-line>
                                    <template v-for="item in list">
                                        <v-subheader v-if="item.header" v-text="item.header" />
                                        <v-divider v-else-if="item.divider" v-bind:inset="item.inset" />
                                        <v-list-item v-else v-bind:key="item.title">
                                            <v-list-tile avatar>
                                                <v-list-tile-avatar>
                                                    <img v-bind:src="item.avatar" />
                                                </v-list-tile-avatar>
                                                <v-list-tile-content>
                                                    <v-list-tile-title v-html="item.title" />
                                                    <v-list-tile-sub-title v-html="item.subtitle" />
                                                </v-list-tile-content>
                                            </v-list-tile>
                                        </v-list-item>
                                    </template>
                                </v-list>
                            </v-card>
                        </div>
                    </v-col>
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
                    <v-col xs12>

                    </v-col>


                </v-col>
            </v-row>
        </v-container>
    </div>
</template>

<script lang="ts">
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import Vue from 'vue';

    @Component({})
    export default class PhenotypeDetail extends Vue {
      @Prop()
      phenotypeId: string;
      phenotypeName: string = 'Flowering time (test)';
      phenotypeDescription: string = 'A study conducted on n samples for phenotype p.';
      genotype: string = 'AtPolyDB (Horton et al.)';
      transformation: string = 'Log10';
      scoring: string = 'Plants were checked bi-weekly for presence of first buds, and the average flowering time of 4 plants of the same accession were collected';
      currentView: string = '';
      columns = ['SNP', 'p-value', 'gene', 'study'];
      n = {phenotypes: 0, accessions: 0};
//    TODO: add linking to studyId through router or linking, usually the id should be given by previous page

      sortOrders = {snp: 1, pvalue: 1, gene: 1, study: 1};
      sortKey: string = '';
      ordered: string = '';
      filterKey: string = '';
      associations = [];
      currentPage = 1;
      pageCount = 5;
      totalCount = 0;
      list: [
        { header: 'Today' },
        { avatar: '...', title: 'Brunch this weekend?', subtitle: '...' },
        { divider: true, inset: true },
        { avatar: '...', title: 'Summer BBQ', subtitle: '...' },
        { divider: true, inset: true },
        { avatar: '...', title: 'Qui Qui', subtitle: '...' }
      ];

      get filteredData() {
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
        this.loadData(this.currentPage);
      }
      loadData(page: number): void {
//            loadStudy(this.studyId, page, this.ordered).then(this._displayData)
      }
      _displayData(data): void {
        this.associations = data.results;
        this.currentPage = data.current_page;
        this.totalCount = data.count;
        this.pageCount = data.page_count;
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
