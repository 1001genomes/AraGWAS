<template>
    <div class="mt-0">
        <v-parallax class="parallax-container" src="/static/img/ara1.jpg" height="80">
            <div class="section">
                <div class="mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                </div>
            </div>
        </v-parallax>
        <div class="page-container">
            <div class="section pa-3">
                <v-layout row class="mb-4">
                    <v-flex xs12><h5 class="green--text mb-2 mt-3"><v-icon class="green--text lighten-1" style="vertical-align: middle;">whatshot</v-icon> Top Genes</h5><v-divider class="mb-3"></v-divider>
                        <span style="font-size: 1.2rem">Check out the genes with most hits across the <em>Arabidopsis thaliana</em> genome. This table shows all top genes (sorted by number of high-scoring hits) that are stored in the database. Genes with 0 hits are not shown.</span></v-flex>
                </v-layout>
               <v-layout wrap column justify-space-around>
                    <div>
                        <v-switch v-model="showFilters" primary hide-details label="Show filters" class="mb-0"></v-switch>
                    </div>
                    <v-flex>
                        <v-layout v-bind="layoutBinding">
                            <div v-bind:open="showFilters" class="pl-1 pr-1 associations-control-container">
                                <div>
                                    <h6 class="mt-4">Significance</h6>
                                    <v-switch
                                            label="Only count significant hits"
                                            v-model="significant"
                                            primary
                                            class="mt-0 mb-0 pt-0" hide-details
                                    ></v-switch>
                                    <div class="ml-3" v-if="significant">
                                        <v-radio-group v-model="threshold" >
                                            <v-radio label="Permutation threshold" value="p" ></v-radio>
                                            <v-radio label="Bonferroni threshold"  value="b" ></v-radio>
                                        </v-radio-group>
                                    </div>
                                    <div>If turned off, all associations with p-value < 10<sup>-4</sup> will be taken into account.</div>
                                </div>
                                <div>
                                    <h6 class="mt-5">Genes per page</h6>
                                    <v-select
                                            v-bind:items="pageSizes"
                                            v-model="pagination.rowsPerPage"
                                            label="Genes per page"
                                            light
                                            single-line
                                            auto hide-details
                                            class="pt-0"
                                    ></v-select>
                                </div>
                                <div>
                                    <h6 class="mt-4">Chromosomes</h6>
                                    <v-checkbox v-model="filters.chr" primary :label="'1 (' + roundPerc(percentage.chromosomes.chr1) + '% of all genes)'" value="1" class="mb-0" hide-details> what</v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'2 (' + roundPerc(percentage.chromosomes.chr2) + '% of all genes)'" value="2" class="mt-0 mb-0" hide-details></v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'3 (' + roundPerc(percentage.chromosomes.chr3) + '% of all genes)'" value="3" class="mt-0 mb-0" hide-details></v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'4 (' + roundPerc(percentage.chromosomes.chr4) + '% of all genes)'" value="4" class="mt-0 mb-0" hide-details></v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'5 (' + roundPerc(percentage.chromosomes.chr5) + '% of all genes)'" value="5" class="mt-0" hide-details></v-checkbox>
                                </div>
                            </div>
                            <v-flex wrap fill-height class="pl-1 pr-1 associations-table-container">
                                <v-data-table
                                        v-bind:headers="headers"
                                        v-bind:items="genes"
                                        v-bind:pagination.sync="pagination"
                                        hide-actions
                                        :loading="loading"
                                        :no-data-text="noDataText"
                                        class="elevation-1 mt-2 asso-table"

                                >
                                    <template slot="headerCell" scope="props">
                                        <span v-tooltip:bottom="{ 'html': props.header.tooltip}">
                                        {{ props.header.text | capitalize }}
                                        </span>
                                    </template>
                                    <template slot="items" scope="props">
                                        <td>
                                            <router-link :to="{name: 'geneDetail', params: { geneId: props.item.name }}">{{ props.item.name }}</router-link></td>
                                        <td>
                                            <div>{{ props.item.nHits }}</div></td>
                                        <td>
                                            <div>{{ props.item.chr[3] }}</div></td>
                                        <td>
                                            <div>{{ props.item.positions.gte }} - {{ props.item.positions.lte }}</div></td>
                                        <td>
                                            <div>{{ props.item.strand }}</div></td>
                                        <td>
                                            <div v-for="isoform in props.item.isoforms">{{ isoform.name }}</div></td>
                                        <td>
                                            <div>{{ props.item.isoforms[0].shortDescription }}</div></td>
                                    </template>
                                </v-data-table>
                                <div class="page-container mt-5 mb-3">
                                    <v-pagination :length="pageCount" v-model="currentPage">
                                    </v-pagination>
                                </div>
                            </v-flex >
                        </v-layout>
                    </v-flex>
               </v-layout>
            </div>
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch} from "vue-property-decorator";

    import Page from "../models/page";
    import Study from "../models/study";
    import Breadcrumbs from "./breadcrumbs.vue"

    import tourMixin from "../mixins/tour.js";

    import {loadTopGenesList, loadTopGenesAggregatedStatistics} from "../api";

    import _ from "lodash";


    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
        components: {
            "breadcrumbs": Breadcrumbs,
        },
        mixins: [tourMixin],
    })
    export default class TopGenes extends Vue {
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Top Genes", href: "#/top-genes", disabled: true}];

        loading: boolean = false;
        noDataText: string = "No data available.";
        headers = [{text: "gene", value: "name", name: "name", align: "left", tooltip: "Name of Gene"},{text: "n hits", value: "nHits", name: "nHits", tooltip: "Number of hits associated with the gene", align: "left"},
            {text: "chr", name: "chromosome", sortable: false, tooltip: "Chromosome", align: "left"},{text: "position",value: "snp.geneName", name: "gene", sortable: false, tooltip: "Genetic range", align: "left"},
            {text: "strand", value: "strand", name: "strand", sortable: true, tooltip: "Strand", align: "left"},{text: "isoforms", name: "isoforms", sortable: false, tooltip: "Isoforms", align: "left"},
            {text: "short description", name: "shortdesc", sortable: false, tooltip: "Short description", align: "left"},];
            // {text: "N KO hits", name: "nKOHits", sortable: false, tooltip: "Number of phenotype hits for K.O. mutations", align: "left"},
            // {text: "KO Mutation hits", name: "koHits", sortable: false, tooltip: "Phenotype associated with K.O. mutations", align: "left"},];
        genes: any[] =[];
        currentPage = 1;
        chr = ["1", "2", "3", "4", "5"];
        significant = true;
        filters = {chr: this.chr, significant: "p"};
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name, sortBy: "nHits", descending: true};
        percentage = {chromosomes: {}, annotations: {}, types: {}, maf: {}};
        debouncedloadData = _.debounce(this.loadData, 300);
        pageSizes = [25, 50, 75, 100, 200,];
        pageCount = 5;
        threshold = 'p';
        showFilters = false;
        readonly showFilterWidth = 1090;

        @Watch("$vuetify.breakpoint")
        onBreakPointChanged() {
            this.showFilters = this.$el.offsetWidth >= this.showFilterWidth;
        }

        @Watch("currentPage")
        onCurrentPageChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("significant")
        onSignificantChanged(val: boolean, oldVal: boolean) {
            if(val) {
                this.filters.significant = this.threshold;
            }
            else {
                this.filters.significant = "0";
            }
        }
        @Watch("threshold")
        onThresholdChanged(val: boolean, oldVal: boolean) {
            this.filters.significant = this.threshold;
        }
        @Watch("filters.significant")
        onFilterChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.chr")
        onChrChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("pagination.rowsPerPage")
        onRowsPerPageChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        mounted(): void {
            this.showFilters = this.$el.offsetWidth >= this.showFilterWidth;
            this.loadData(this.currentPage);
        }
        loadData(pageToLoad): void {
            this.loading = true;
            this.noDataText = "Data is loading...";
            // Need to check for already visited pages
            loadTopGenesList(this.filters, pageToLoad, this.pagination.rowsPerPage).then(this._displayData);
            loadTopGenesAggregatedStatistics(this.filters).then(this._displayAggregatedData);
        }
        _displayAggregatedData(data): void {
            this.percentage = data;
        }
        _displayData(data): void {
            this.genes = data.results;
            this.pagination.totalItems = data.count;
            this.pageCount = Math.ceil(data.count/this.pagination.rowsPerPage);
            this.loading = false;
            this.noDataText = "No data available.";
        }
        roundPerc(number): number {
            if (isNaN(number)) {
                return 0.0
            }
            return Math.round(number * 1000) / 10;
        }

        get layoutBinding() {
            const binding = {}

            if ((<any>this)['$vuetify']['breakpoint']['xsOnly']) binding['wrap'] = true;
            else  binding['row'] = true;
            return binding
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="stylus">

    .section {
        width:100%;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }
    .associations-control-container {
        flex: 0 0 360px;
        display:none;
    }

    .associations-control-container[open] {
        display:block;
    }
    .associations-table-container {
        min-width: 0;
    }
</style>
