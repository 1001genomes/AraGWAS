<template>
    <v-layout row wrap>
        <v-flex xs12>
            <breadcrumbs :breadcrumbsItems="breadcrumbs"></breadcrumbs>
        </v-flex>
        <v-flex xs12 sm4 class="pl-4 pr-4">
            <gene-search v-model="selectedGene" class="gene-search"></gene-search>
        </v-flex>
        <v-flex xs12 sm4 offset-sm4 class="pl-4 pr-4">
            <div style="width:300px;" class="gene-zoom">
                <v-slider v-model="zoom" prepend-icon="zoom_in" permanent-hint hint="Zoom" max="20" min="0"  ></v-slider>
            </div>
        </v-flex>
        <v-flex xs12>
            <gene-plot class="flex" :genes="genes" :region="region" :options="options" :associations="associations" :highlightedAssociations="highlightedAssociations"></gene-plot>
        </v-flex>
        <v-flex xs12 class="pl-4 pr-4">
            <div >
                    <h5 class="mb-1 gene-associations">Associations List</h5>
                    <v-divider></v-divider>
                    <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields" :view="geneView" v-model="associations" v-on:load="onLoadAssociations" v-on:association="onHighlightAssocInTable" ></top-associations>
            </div>
        </v-flex>
    </v-layout >
</template>

<script lang="ts">
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import GenePlot from "../components/geneplot.vue";
    import GeneSearch from "../components/geneSearch.vue";
    import Breadcrumbs from "./breadcrumbs.vue"
    import Router from "../router";
    import TopAssociationsComponent from "./topasso.vue"

    import {loadAssociationsOfGene, loadGene, loadGenesByRegion} from "../api";

    import Association from "../models/association"
    import Gene, {GenePlotOptions} from "../models/gene";

    import tourMixin from "../mixins/tour.js";

    import _ from "lodash";

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
        mixins: [tourMixin],
    })
    export default class GeneDetail extends Vue {
        // Gene information
        router = Router;
        @Prop()
        geneId: string;
        selectedGene: Gene = {id: '', name: '', strand: '',chr: '', type: '', positions: {gte: 0, lte: 0 }};
        searchTerm: string = "";
        associationCount = 0;
        genes: Gene[] = [];

        // Associations parameters
        ordered: string;
        zoom = 0;
        pageCount = 5;
        currentPage = 1;
        totalCount = 0;
        columns = ["SNP", "score", "phenotype", "gene", "maf", "beta", "odds ratio", "confidence interval"];
        filterKey: string = "";
        associations = [];
        highlightedAssociations: Association[] = [];


        maf = ["5-10", "10"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        chr = ["1", "2","3","4","5"];
        hideFields = [];
        showControls = ["maf","annotation","type"];
        filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, type: this.type};
        deboundedLoadGenes = _.debounce(this.loadGenesInRegion, 300);

        get startRegion(): number  {
            if (this.selectedGene) {
                return this.selectedGene.positions.gte - this.zoom * 1000 / 2;
            }
            return 0;
        }
        get endRegion(): number   {
            if (this.selectedGene) {
                return this.selectedGene.positions.lte + this.zoom * 1000 / 2 ;
            }
            return 0;
        }

        get region(): number[] {
            return [this.startRegion, this.endRegion];
        }

        get options(): GenePlotOptions {
            const zoom = this.zoom * 1000 / 2;
            const chr = this.selectedGene.chr;
            const maxScore = 15;
            const bonferoniThreshold = 5;
            return new GenePlotOptions(chr, this.startRegion, this.endRegion, maxScore, bonferoniThreshold);
        }

        get breadcrumbs() {
            return [{text: "Home", href: "/"}, {text: "Genes", href: "genes", disabled: true}, {text: this.selectedGene ? this.selectedGene.id : "", href: "", disabled: true}];
        }

        get geneView() {
            return {name: "gene", geneId: this.geneId, zoom: this.zoom * 1000 / 2};
        }

        onLoadAssociations(associations) {
            this.associations = associations
        }

        onHighlightAssocInTable(association: Association) {
            // TODO use array operators
            this.highlightedAssociations = [association];
        }

        @Watch("selectedGene")
        onSelectedGeneChanged(val, oldVal) {
            if (oldVal === null || val.id !== oldVal.id) {
                this.$router.push({ name: 'geneDetail', params: { geneId: val.id }})
                this.loadGenesInRegion();
            }
        }

        @Watch("geneId")
        onGeneIdChanged(val: number, oldVal: number) {
            this.loadData();
        }

        @Watch("zoom")
        onZoomChanged() {
            this.deboundedLoadGenes();
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
                loadGene(this.geneId)
                    .then((gene) => {
                        this.selectedGene = gene
                });
            } catch (err) {
                console.log(err);
            }
        }

        loadGenesInRegion(): void {
            loadGenesByRegion(this.selectedGene.chr, this.startRegion, this.endRegion, true).then( (genes) => this.genes = genes);
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

        tourOptions = {
            steps: [
                {
                    element: ".gene-search",
                    intro: "The search bar allows you to jump to any other gene stored in the Database.",
                    position: "right"
                },
                {
                    element: ".gene-plot",
                    intro: "This genomic region view shows significant associations linked with the gene of interest.",
                    position: "top"
                },
                {
                    element: ".gene-zoom",
                    intro: "You can use the zoom to show further associations linked to this gene",
                    position: "left"
                },
                {
                    element: ".gene-associations",
                    intro: "This is a list of the associations shown above.",
                    position: "top"
                },
                {
                    element: ".aragwas-logo",
                    intro: "This is the end of the tour. Enjoy AraGWAS Catalog!",
                    position: "bottom"
                }
            ],
        };
    }
</script>
<style scoped>
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>
