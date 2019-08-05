<template>
    <div class="mt-0">
        <v-parallax class="parallax-container" src="/static/img/ara2.jpg" height="80">
            <div class="section">
                <div class="breadcrumbs-container mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                </div>
            </div>
        </v-parallax>
        <div class="page-container">
            <div class="section pa-3">
                <v-layout row class="mb-4">
                    <v-flex xs12><h5 class="green--text mb-2 mt-3"><v-icon class="green--text lighten-1" style="vertical-align: middle;">flash_off</v-icon> Top KO Mutations</h5><v-divider class="mb-3"></v-divider>
                        <span style="font-size: 1.2rem">Check out the top KO mutations across the <em>Arabidopsis thaliana</em> genome. This table shows all the KO mutations associated with a phenotype (sorted by score, i.e. - log<sub>10</sub>(p-value)) that are stored in the database. Significant associations are marked in blue.</span></v-flex>
                </v-layout>
                <v-layout wrap column justify-space-around>
                    <div>
                        <v-switch v-model="showFilters" primary hide-details label="Show filters" class="mb-0"></v-switch>
                    </div>
                    <v-flex>
                        <v-layout v-bind="layoutBinding">
                            <div v-bind:open="showFilters" class="pl-1 pr-1 associations-control-container">
                                <div>
                                    <h6 class="mt-5">Mutations per page</h6>
                                    <v-select
                                            v-bind:items="pageSizes"
                                            v-model="pagination.rowsPerPage"
                                            label="Mutations per page"
                                            light
                                            single-line
                                            auto hide-details
                                            class="pt-0"
                                    ></v-select>
                                </div>
                                <div>
                                    <h6 class="mt-4">Chromosomes</h6>
                                    <v-checkbox v-model="filters.chr" primary :label="'1'" value="1" class="mb-0" hide-details> what</v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'2'" value="2" class="mt-0 mb-0" hide-details></v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'3'" value="3" class="mt-0 mb-0" hide-details></v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'4'" value="4" class="mt-0 mb-0" hide-details></v-checkbox>
                                    <v-checkbox v-model="filters.chr" primary :label="'5'" value="5" class="mt-0" hide-details></v-checkbox>
                                </div>
                            </div>
                            <v-flex wrap fill-height class="pl-1 pr-1 associations-table-container">
                                <v-data-table
                                        v-bind:headers="headers"
                                        v-bind:items="mutations"
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
                                            <router-link v-if="typeof props.item.gene.isoforms !== 'undefined'" :to="{name: 'geneDetail', params: { geneId: props.item.gene.name }}">{{ props.item.gene.name }}</router-link>
                                            <div v-else>{{ props.item.gene.name }} </div></td>
                                        <td class='blue--text'>
                                            <div>{{ Math.round(props.item.score*100)/100 }}</div></td>
                                        <td>
                                            <router-link :to="{name: 'studyDetail', params: { id: props.item.study.id }}">{{ props.item.study.phenotype.name }}</router-link>
                                        <td>
                                            <div v-if="typeof props.item.gene.isoforms === 'undefined'">{{ props.item.gene.name[2] }}</div>
                                            <div v-else> {{ props.item.gene.chr[3] }}</div></td>
                                        <td v-if="typeof props.item.gene.positions !== 'undefined'">
                                            <div>{{ props.item.gene.positions.gte }} - {{ props.item.gene.positions.lte }}</div>
                                        <td v-else>
                                            <div>-</div></td>
                                        <td v-if="typeof props.item.gene.strand !== 'undefined'">
                                            <div>{{ props.item.gene.strand }}</div>
                                        <td v-else>
                                            <div></div></td>
                                        <td>
                                            <div>{{ Math.round(props.item.maf*1000)/1000 }}</div></td>
                                        <td>
                                            <div>{{ props.item.mac }}</div></td>
                                        <td v-if="typeof props.item.gene.isoforms !== 'undefined'">
                                            <div v-for="isoform in props.item.gene.isoforms">{{ isoform.name }}</div></td>
                                        <td v-else>
                                            <div>-</div></td>
                                        <td v-if="typeof props.item.gene.isoforms !== 'undefined'">
                                            <div>{{ props.item.gene.isoforms[0].shortDescription | capitalize }}</div></td>
                                        <td v-else>
                                            <div>-</div></td>    
                                    </template>
                                </v-data-table>
                                <div class="page-container mt-5 mb-3">
                                    <div>
                                        <v-btn floating secondary @click="previous" :disabled="pager===1"><v-icon light>keyboard_arrow_left</v-icon></v-btn>
                                        <v-btn floating secondary @click="next" :disabled="pager===pageCount"><v-icon light>keyboard_arrow_right</v-icon></v-btn>
                                    </div>
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
    import KOAssociation from "../models/koassociation";
    import Breadcrumbs from "./breadcrumbs.vue"

    import {loadTopKOMutations} from "../api";
    import _ from "lodash";

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
        components: {
            "breadcrumbs": Breadcrumbs
        }
    })
    export default class TopKOMutations extends Vue {
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Top KO Mutations", href: "#/top-ko-mutations", disabled: true}];

        loading: boolean = false;
        noDataText: string = "No data available.";
        headers = [{text: "gene",value: "snp.geneName", name: "gene", sortable: false, tooltip: "Gene name", align: "left"},
            {text: "score", value: "score", name: "score", tooltip: "KO mutation association score", align: "left"},
            {text: "Study", name: "study", sortable: false, tooltip: "Phenotype associated with the KO mutation", align: "left"},
            {text: "chr", name: "chromosome", sortable: false, tooltip: "Chromosome", align: "left"},
            {text: "position",value: "snp.geneName", name: "gene", sortable: false, tooltip: "Genetic range", align: "left"},
            {text: "strand", value: "strand", name: "strand", sortable: false, tooltip: "Strand", align: "left"},
            {text: "MKF", value: "maf", name: "maf", sortable: false, tooltip: "Minor knockout frequency", align: "left"},
            {text: "MKC", value: "mac", name: "mac", sortable: false, tooltip: "Minor knockout count", align: "left"},
            {text: "isoforms", name: "isoforms", sortable: false, tooltip: "Isoforms", align: "left"},
            {text: "short description", name: "shortdesc", sortable: false, tooltip: "Short description", align: "left"}];
            
        mutations: KOAssociation[] =[];
        chr = ["1", "2", "3", "4", "5"];
        significant = true;
        filters = {chr: this.chr, significant: "p"};
        pager = 1;
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name, sortBy: "nHits", descending: true};
        debouncedloadData = _.debounce(this.loadData, 300);
        pageSizes = [25, 50, 75, 100, 200,];
        pageCount = 5;
        threshold = 'p';
        showFilters = false;
        lastElement: [number, string];
        lastElementHistory = {'1': [0,''], };
        readonly showFilterWidth = 1090;

        @Watch("$vuetify.breakpoint")
        onBreakPointChanged() {
            this.showFilters = this.$el.offsetWidth >= this.showFilterWidth;
        }
        @Watch("filters.significant")
        onFilterChanged(val: number, oldVal: number) {
            this.debouncedloadData(1);
        }
        @Watch("filters.chr")
        onChrChanged(val: number, oldVal: number) {
            this.debouncedloadData(1);
        }
        @Watch("pagination.rowsPerPage")
        onRowsPerPageChanged(val: number, oldVal: number) {
            this.debouncedloadData(1);
        }
        mounted(): void {
            // this.showFilters = this.$el.offsetWidth >= this.showFilterWidth;
            this.loadData(this.pager);
        }
        previous(): void {
            if (this.pager > 1) {
                this.pager -= 1;
                this.loadData(this.pager);
            }
        }
        next(): void {
            this.pager += 1;
            this.lastElementHistory[this.pager.toString()] = this.lastElement;
            this.loadData(this.pager);
        }
        loadData(pageToLoad): void {
            this.loading = true;
            this.noDataText = "Data is loading...";
            // Need to check for already visited pages
            loadTopKOMutations(this.filters, pageToLoad, this.pagination.rowsPerPage, this.lastElementHistory[pageToLoad.toString()]).then(this._displayData);
            this.pager = pageToLoad;
        }
        _displayData(data): void {
            this.mutations = data.results;
            this.pagination.totalItems = data.count;
            this.pageCount = Math.ceil(data.count/this.pagination.rowsPerPage);
            this.loading = false;
            this.noDataText = "No data available.";
            this.lastElement = data.lastel;
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
<style scoped>
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
