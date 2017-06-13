<template>
    <v-layout column>
        <v-flex xs12>
            <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
        </v-flex>
        <v-flex xs12 sm4>
            <gene-search v-model="selectedGene"></gene-search>
        </v-flex>
        <v-flex xs12>
            <v-layout row justify-space-around>
                <div>
                    <h5 class="mb-1">Genomic Region : {{ selectedGene.name }}</h5>
                    <v-divider></v-divider>
                </div>
                <div class="flex"></div>
                <div style="width:300px;">
                    <v-slider v-model="zoom" prepend-icon="zoom_in" permanent-hint hint="Zoom" :min="min" ></v-slider>
                </div>
            </v-layout>
        </v-flex>
        <v-flex xs12>
            <gene-plot class="flex" :options="options"></gene-plot>
        </v-flex>
        <v-flex xs12>
            <h5 class="mb-1">Associations List</h5>
            <v-divider></v-divider>
            <v-card class="mt-3">
                <table class="table">
                    <thead>
                    <tr>
                        <th v-for="key in columns">
                            {{ key | capitalize }}
                        </th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="entry in filteredData">
                        <td v-for="key in columns">
                            <div>{{entry[key]}}</div>
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
</template>

<script lang="ts">
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import GenePlot from "../components/geneplot.vue";
    import GeneSearch from "../components/geneSearch.vue";
    import Breadcrumbs from "./breadcrumbs.vue"
    import Router from "../router";

    import {loadAssociationsOfGene, loadGene} from "../api";
    import Gene from "../models/gene";

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
        components: {
            "gene-plot": GenePlot,
            "gene-search": GeneSearch,
            "breadcrumbs": Breadcrumbs,
        },
    })
    export default class GeneDetail extends Vue {
        // Gene information
        router = Router;
        @Prop()
        geneId: string;
        selectedGene: Gene = {id: '', name: '', strand: '',chr: '', type: '', positions: {gte: 0, lte: 0 }}
        searchTerm: string = "";
        associationCount = 0;
        min = 10;

        // Associations parameters
        ordered: string;
        zoom = 75;
        pageCount = 5;
        currentPage = 1;
        totalCount = 0;
        columns = ["SNP", "p-value", "phenotype", "gene", "maf", "beta", "odds ratio", "confidence interval"];
        filterKey: string = "";
        associations = [];

        get options() {
            return {
                width: 1000,
                min_x: 1200000,
                max_x: 1289300,
                gene: this.selectedGene,
                w_rect: 0,
                zoom: this.zoom,
            };
        }

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

        get breadcrumbs() {
            return [{text: "Home", href: "home"}, {text: "Genes", href: "genes"}, {text: this.selectedGene ? this.selectedGene.id : "", href: "", disabled: true}];
        }

        @Watch("selectedGene")
        onSelectedGeneChanged(val, oldVal) {
            if (oldVal === null || val.id !== oldVal.id) {
                this.$router.push({ name: 'geneDetail', params: { geneId: val.id }})
            }
        }

        @Watch("geneId")
        onGeneIdChanged(val: number, oldVal: number) {
            this.loadData();
        }

        created(): void {
            this.loadData();
        }

        // Gene DATA LOADING
        _displayGeneData(data: Gene): void {
            this.selectedGene = data;
        }
        // ASSOCIATION LOADING
        loadData(): void {
            // Load associations of all cited SNPs
            try {
                loadGene(this.geneId).then(this._displayGeneData);
                loadAssociationsOfGene(this.geneId, this.currentPage, this.ordered).then(this._displayData);
            } catch (err) {
                console.log(err);
            }
        }
        _displayData(data): void {
            this.associations = data.results;
            this.currentPage = data.current_page;
            this.totalCount = data.count;
            this.pageCount = data.page_count;
        }
        goToGene(): void {
            this.router.push({name: "geneDetail", params: { geneId: this.searchTerm }});
        }
    }
</script>
<style scoped>
    .page-container {
        display:flex;
        justify-content:center;
    }
    ul.breadcrumbs {
        padding-left:0;
    }
</style>
