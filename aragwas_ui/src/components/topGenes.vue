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
            <div class="section">
                <v-layout row class="mb-4">
                    <v-flex xs12><h5 class="mb-2 mt-3"><v-icon class="green--text lighten-1" style="vertical-align: middle;">whatshot</v-icon> Top Genes</h5><v-divider class="mb-3"></v-divider>
                        <span style="font-size: 1.2rem">Check out the genes with most hits across the <em>Arabidopsis thaliana</em> genome. This table shows all top genes (sorted by number of high-scoring hits) that are stored in the database. Genes with 0 hits are not shown.</span></v-flex>
                </v-layout>
                <v-layout row-xs child-flex-xs wrap justify-space-around>
                    <v-flex xs3 wrap class="associations-control-container">
                        <div>
                            <h6 class="mt-4">Genes per page</h6>
                            <v-select
                                    v-bind:items="pageSizes"
                                    v-model="pagination.rowsPerPage"
                                    label="Genes per page"
                                    dark
                                    single-line
                                    auto
                            ></v-select>
                        </div>
                        <div>
                            <h6 class="mt-4">Chromosomes</h6>
                            <v-checkbox v-model="filters.chr" primary :label="'1 (' + roundPerc(percentage.chromosomes.chr1) + '% of all genes)'" value="1" class="mb-0"> what</v-checkbox>
                            <v-checkbox v-model="filters.chr" primary :label="'2 (' + roundPerc(percentage.chromosomes.chr2) + '% of all genes)'" value="2" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="filters.chr" primary :label="'3 (' + roundPerc(percentage.chromosomes.chr3) + '% of all genes)'" value="3" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="filters.chr" primary :label="'4 (' + roundPerc(percentage.chromosomes.chr4) + '% of all genes)'" value="4" class="mt-0 mb-0"></v-checkbox>
                            <v-checkbox v-model="filters.chr" primary :label="'5 (' + roundPerc(percentage.chromosomes.chr5) + '% of all genes)'" value="5" class="mt-0"></v-checkbox>
                        </div>
                    </v-flex>
                    <v-flex xs9 wrap fill-height class="association-table-container">
                        <v-data-table
                                v-bind:headers="headers"
                                v-bind:items="genes"
                                v-bind:pagination.sync="pagination"
                                hide-actions
                                :loading="loading"
                                class="elevation-1 mt-2 asso-table"

                        >
                            <template slot="headers" scope="props">
                                <span v-tooltip:bottom="{ 'html': props.item.tooltip}">
                                  {{ props.item.text | capitalize }}
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
        headers = [{text: "gene", value: "name", name: "name", left: true, tooltip: "Name of Gene"},{text: "n hits", value: "nHits", name: "nHits", tooltip: "Number of hits associated with the gene", left: true},
            {text: "chr", name: "chromosome", sortable: false, tooltip: "Chromosome", left: true},{text: "position",value: "snp.geneName", name: "gene", sortable: false, tooltip: "Genetic range", left: true},
            {text: "strand", value: "strand", name: "strand", sortable: true, tooltip: "Strand", left: true},{text: "isoforms", name: "isoforms", sortable: false, tooltip: "Isoforms", left: true},
            {text: "short description", name: "shortdesc", sortable: false, tooltip: "Short description", left: true}];
        genes: any[] =[];
        currentPage = 1;
        chr = ["1", "2", "3", "4", "5"];
        filters = {chr: this.chr};
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name, sortBy: "nHits", descending: true};
        percentage = {chromosomes: {}, annotations: {}, types: {}, maf: {}};
        debouncedloadData = _.debounce(this.loadData, 300);
        pageSizes = [25, 50, 75, 100, 200,];
        pageCount = 5;


        @Watch("currentPage")
        onCurrentPageChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.maf")
        onMafChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.chr")
        onChrChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.annotation")
        onAnnotationChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.type")
        onTypeChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("pagination.rowsPerPage")
        onRowsPerPageChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        mounted(): void {
            this.loadData(this.currentPage);
        }
        loadData(pageToLoad): void {
            this.loading = true;
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
        }
        roundPerc(number): number {
            if (isNaN(number)) {
                return 0.0
            }
            return Math.round(number * 1000) / 10;
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .section {
        width: 90%;
        padding-top: 1rem;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>