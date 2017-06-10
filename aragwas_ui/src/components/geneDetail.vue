<template>
    <v-layout column>
        <v-flex xs12>
             <v-breadcrumbs icons divider="chevron_right" class="left">
                <v-breadcrumbs-item
                        v-for="item in breadcrumbs" :key="item"
                        :disabled="item.disabled"
                        class="breadcrumbsitem"
                        :href="{name: item.href}"
                        router
                >
                    <span :class="['title', {'green--text': !item.disabled}]">{{ item.text}}</span>
                </v-breadcrumbs-item>
            </v-breadcrumbs>
            <v-divider></v-divider>
        </v-flex>
        <v-flex xs12 sm4>
            <v-text-field name="geneName-search" :label="geneName" v-model="searchTerm" prepend-icon="search" single-line><input type="search" @keyup.enter="goToGene()"></v-text-field>
        </v-flex>
        <v-flex xs12>
            <v-layout row justify-space-around>
                <div>
                    <h5 class="mb-1">Genomic Region : {{ geneName }}</h5>
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
    import {loadAssociationsOfGene, loadGene} from "../api";
    import GenePlot from "../components/geneplot.vue";
    import Router from "../router";

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
        },
        components: {
            "gene-plot": GenePlot,
        },
    })
    export default class GeneDetail extends Vue {
        // Gene information
        router = Router;
        @Prop()
        geneId: string;
        searchTerm: string = "";
        geneName: string = "";
        geneDescription: string = "";
        startPosition = 0;
        endPosition = 1;
        centerOfGene = 0;
        snpSet;
        snpCount = 0;
        associationCount = 0;
        windowStartPosition = 0;
        windowEndPosition = 0;
        min = 10;
        get options() {
            return {
                width: 1000,
                min_x: 1200000,
                max_x: 1289300,
                chr: undefined,
                w_rect: 0,
            };
        }
        // Associations parameters
        ordered: string;
        breadcrumbs = [{text: "Home", href: "home"}, {text: "Genes", href: "genes"}, {text: this.geneName, href: "", disabled: true}];
        zoom = 75;
        pageCount = 5;
        currentPage = 1;
        totalCount = 0;
        columns = ["SNP", "p-value", "phenotype", "gene", "maf", "beta", "odds ratio", "confidence interval"];
        filterKey: string = "";
        associations = [];

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
        @Watch("geneId")
        onGeneIdChanged(val: number, oldVal: number) {
            this.loadData();
        }

        @Watch("zoom")
        onZoomChanged(val: number, oldVal: number) {
            this.$nextTick(function() {
                this.updateGeneRegion();
            });
        }

        created(): void {
            this.loadData();
        }

        // Gene DATA LOADING
        _displayGeneData(data): void {
            this.geneName = data.gene.name;
            this.breadcrumbs[2].text = data.name;
//            this.startPosition = data.start_position;
//            this.endPosition = data.end_position;
            this.options.chr = data.gene.chr;
            this.options.w_rect = data.gene.positions.lte - data.gene.positions.gte;
            this.centerOfGene = data.gene.positions.gte + this.options.w_rect / 2;
            this.snpSet = data.snps;
            this.snpCount = data.snp_count;
            this.associationCount = data.associationCount;
        }
        // ASSOCIATION LOADING
        loadData(): void {
            // Load associations of all cited SNPs
            try {
                loadGene(this.geneId).then(this._displayGeneData);
                loadAssociationsOfGene(this.geneId, this.currentPage, this.ordered).then(this._displayData);
                this.centerOfGene = this.startPosition + (this.endPosition - this.startPosition) / 2;
                this.updateGeneRegion();
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
        updateGeneRegion(): void {
            const windowsize = Math.round((this.endPosition - this.startPosition) * 100 / this.zoom);
            this.windowStartPosition = this.centerOfGene - windowsize / 2;
            this.windowEndPosition = this.centerOfGene + windowsize / 2;
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
