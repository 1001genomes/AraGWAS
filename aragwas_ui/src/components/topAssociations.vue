<template>
    <div class="mt-0">
        <v-parallax class="parallax-container" src="/static/img/ara5.jpg" height="80">
            <div class="section">
                <div class="container mt-2">
                    <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
                </div>
            </div>
        </v-parallax>
        <div class="container">
            <div class="section">
                <v-container fluid>
                    <v-layout row>
                        <v-flex xs12><h5 class="mb-2 mt-3"><v-icon class="green--text lighten-1" style="vertical-align: middle;">trending_up</v-icon> Top Associations</h5><v-divider></v-divider></v-flex>
                    </v-layout>
                    <v-layout row wrap>
                        <v-flex xs3 wrap>
                            <h6 class="mt-4">MAF</h6>
                                <v-switch v-model="maf" primary label="<1% ( % of SNPs)" value="1" class="mb-0"></v-switch>
                                <v-checkbox v-model="maf" primary label="1-5% ( % of SNPs)" value="1-5" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="maf" primary label="5-10% ( % of SNPs)" value="5-10" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="maf" primary label=">10% ( % of SNPs)" value="10" class="mt-0"></v-checkbox>
                            <h6 class="mt-4">Chromosomes</h6>
                                <v-checkbox v-model="chr" warning label="1 ( % of SNPs)" value="1" class="mb-0"></v-checkbox>
                                <v-checkbox v-model="chr" primary label="2 ( % of SNPs)" value="2" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="chr" info label="3 ( % of SNPs)" value="3" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="chr" error label="4 ( % of SNPs)" value="4" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="chr" label="5 ( % of SNPs)" value="5" class="mt-0"></v-checkbox>
                            <h6 class="mt-4">Annotation</h6>
                                <v-checkbox v-model="annotation" primary label="Non-synonymous coding ( % of SNPs)" value="ns" class="mb-0"></v-checkbox>
                                <v-checkbox v-model="annotation" primary label="Synonymous coding ( % of SNPs)" value="s" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="annotation" primary label="Intron ( % of SNPs)" value="in" class="mt-0 mb-0"></v-checkbox>
                                <v-checkbox v-model="annotation" primary label="Intergenic ( % of SNPs)" value="i" class="mt-0 mb-0"></v-checkbox>
                            <h6 class="mt-4">Type</h6>
                                <v-checkbox v-model="type" primary label="Genic ( % of SNPs)" value="genic" class="mb-0"></v-checkbox>
                                <v-checkbox v-model="type" primary label="Non-genic ( % of SNPs)" value="non-genic" class="mt-0 mb-0"></v-checkbox>
                        </v-flex>
                        <v-flex xs9 wrap>
                            <v-data-table
                                    v-bind:headers="columns"
                                    v-bind:items="associations"
                                    v-bind:pagination.sync="pagination"
                                    hide-actions
                                    :loading="loading"
                                    class="elevation-1 mt-2"
                            >
                                <template slot="headers" scope="props">
                                    <span v-tooltip:bottom="{ 'html': props.item.text }">
                                      {{ props.item.text | capitalize }}
                                    </span>
                                </template>
                                <template slot="items" scope="props">
                                    <td v-if="'snp' in props.item ">{{ props.item.snp.chr | capitalize }}:{{ props.item.snp.position }}</td> <td v-else>Missing info</td>
                                    <td  class="text-xs-right">{{ props.item.score | round }}</td>
                                    <td  class="text-xs-right"><router-link :to="{name: 'phenotypeDetail', params: { id: props.item.study.phenotype.id }}">{{ props.item.study.phenotype.name }}</router-link></td>
                                    <td  class="text-xs-right" v-if="'snp' in props.item "><router-link :to="{name: 'geneDetail', params: { geneId: props.item.snp.geneName }}">{{ props.item.snp.geneName }}</router-link></td><td v-else class="text-xs-right">Missing info</td>
                                    <td  class="text-xs-right">{{ props.item.maf | round }}</td>
                                    <td  class="text-xs-right"><router-link :to="{name: 'studyDetail', params: { id: props.item.study.id }}">{{ props.item.study.name }}</router-link></td>
                                </template>
                            </v-data-table>
                            <div class="page-container mt-5 mb-3">
                                <v-pagination :length.number="pageCount" v-model="currentPage" />
                            </div>
                        </v-flex>
                    </v-layout>
                </v-container>
            </div>
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch} from "vue-property-decorator";

    import {loadTopAssociations} from "../api";
    import Page from "../models/page";
    import Study from "../models/study";
    import Breadcrumbs from './breadcrumbs.vue'

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
            round(number) {
                return Math.round( number * 1000) / 1000;
            }
        },
        components: {
            "breadcrumbs": Breadcrumbs,
        },
    })
    export default class TopAssociations extends Vue {
        loading: boolean = false;
        columns = [{text: "SNP", value: "snp.chr"},{text: "score", value: "score"},{text: "phenotype",value: "study.phenotype.name"},{text: "gene",value: "snp.geneName"},{text: "maf",value: "maf"},{text: "study", value: "study.name"}];
        associations = [];
        currentPage = 1;
        pageCount = 5;
        totalCount = 0;
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Top Associations", href: "#/top-associations", disabled: true}];
        maf = ["1", "1-5", "5-10", "10"];
        chr = ["1", "2", "3", "4", "5"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name, sortBy: 'score', descending: true};

        @Watch("currentPage")
        onCurrentPageChanged(val: number, oldVal: number) {
            this.loadData(this.currentPage);
        }
        @Watch("maf")
        onMafChanged(val: number, oldVal: number) {
            this.loadData(this.currentPage);
        }
        @Watch("chr")
        onChrChanged(val: number, oldVal: number) {
            this.loadData(this.currentPage);
        }
        @Watch("annotation")
        onAnnotationChanged(val: number, oldVal: number) {
            this.loadData(this.currentPage);
        }
        @Watch("type")
        onTypeChanged(val: number, oldVal: number) {
            this.loadData(this.currentPage);
        }
        created(): void {
            this.loadData(this.currentPage);
        }
        loadData(pageToLoad): void {
            this.loading = true;
            loadTopAssociations({chr: this.chr, annotation: this.annotation, maf: this.maf, type: this.type}, pageToLoad).then(this._displayData); // change this with ES search
        }
        _displayData(data): void {
            this.associations = data.results;
            this.currentPage = data.currentPage;
            this.totalCount = data.count;
            this.pageCount = data.pageCount;
            this.loading = false;
        }

    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    .banner-container {
        position: relative;
        overflow: hidden;
    }
    .section {
        padding-top: 1rem;
    }
    .table {
        width: 100%;
        max-width: 100%;
        margin-bottom: 2rem;
    }
    /*.parallax-container  {*/
        /*position:absolute;*/
        /*top:0;*/
        /*left:0;*/
        /*right:0;*/
        /*bottom:0;*/
        /*z-index:-1;*/
    /*}*/
    .arrow {
        display: inline-block;
        vertical-align: middle;
        width: 0;
        height: 0;
        margin-left: 5px;
        opacity: 0;
    }

    .arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid green;
    }

    .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid green;
    }

    th.active {
        color:black;
    }

    th.active .arrow {
        opacity: 1;
    }
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>
