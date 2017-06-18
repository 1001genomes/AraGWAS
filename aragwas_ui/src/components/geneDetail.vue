<template>
    <v-layout column>
        <v-flex xs12>
            <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
        </v-flex>
        <v-flex xs12 sm4 class="pl-4 pr-4">
            <gene-search v-model="selectedGene"></gene-search>
        </v-flex>
        <v-flex xs12 class="pl-4 pr-4">
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
        <v-flex xs12 class="pl-4 pr-4">
            <gene-plot class="flex" :options="options"></gene-plot>
        </v-flex>
        <v-flex xs12 class="pl-4 pr-4">
            <div class="container">
                <div class="section">
                    <h5 class="mb-1">Associations List</h5>
                    <v-divider></v-divider>
                    <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields"></top-associations>
                </div>
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
    import TopAssociationsComponent from "./topasso.vue"

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
            "top-associations": TopAssociationsComponent,
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
        columns = ["SNP", "score", "phenotype", "gene", "maf", "beta", "odds ratio", "confidence interval"];
        filterKey: string = "";
        associations = [];


        maf = ["1", "1-5", "5-10", "10"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        chr = ["1", "2","3","4","5"];
        hideFields = [];
//        TODO: add position in filter for associations listing.
        showControls = ["maf","annotation","type"];
        filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, type: this.type};

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
            this.filters.chr = [this.selectedGene.chr[3]]
        }
        // ASSOCIATION LOADING
        loadData(): void {
            // Load associations of all cited SNPs
            try {
                loadGene(this.geneId).then(this._displayGeneData);
            } catch (err) {
                console.log(err);
            }
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
