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
            <gene-plot class="flex" :genes="genes" :options="options" :associations="associations" :highlightedAssociations="highlightedAssociations" v-on:drawn="onDrawn" v-on:highlightgene="onHighlightGene" v-on:unhighlightgene="onUnhighlightGene" v-on:highlightassociations="onHighlightAssociations" v-on:unhighlightassociations="onUnhighlightAssociations"></gene-plot>
        </v-flex>
        <v-flex xs12 class="pl-4 pr-4">
            <div >
                    <h5 class="mb-1 gene-associations">Associations List</h5>
                    <v-divider></v-divider>
                    <top-associations :showControls="showControls" :filters="filters" :hideFields="hideFields" :view="geneView" :highlightedAssociations="highlightedAssociations" v-on:loaded="onLoadAssociations" v-on:association="onHighlightAssocInTable" v-on:loading="onLoading"></top-associations>
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
        @Prop()
        geneOnly: string;
        selectedGene: Gene = {id: '', name: '', strand: '',chr: '', type: '', positions: {gte: 0, lte: 0 }};
        searchTerm: string = "";
        associationCount = 0;
        genes: Gene[] = [];

        // Associations parameters
        ordered: string;
        zoom = 10;
        pageCount = 5;
        currentPage = 1;
        totalCount = 0;
        columns = ["SNP", "score", "phenotype", "gene", "maf", "beta", "odds ratio", "confidence interval"];
        filterKey: string = "";
        associations = [];
        highlightedAssociations: Association[] = [];


        maf = ["1","1-5","5-10", "10"];
        mac = ["5"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        chr = ["1", "2","3","4","5"];
        hideFields = ["phenotype"];
        showControls = ["maf","annotation","type", "pageSize","mac","significant",'geneonly'];
        filters = {chr: this.chr, annotation: this.annotation, maf: this.maf, mac: this.mac, type: this.type, significant: "0", gene: "1"};
        deboundedLoadGenes = _.debounce(this.loadGenesInRegion, 300);
        loadingAsso = false;

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
            const bonferoniThreshold = 8;
            return new GenePlotOptions(chr, this.startRegion, this.endRegion, maxScore, bonferoniThreshold);
        }

        get breadcrumbs() {
            return [{text: "Home", href: "/"}, {text: "Genes", href: "/top-genes"}, {text: this.selectedGene ? this.selectedGene.id : "", href: "", disabled: true}];
        }

        get geneView() {
            return {name: "gene", geneId: this.geneId, zoom: this.zoom * 1000 / 2};
        }

        onHighlightAssociations(associations) {
            this.highlightedAssociations = associations;
        }
        onUnhighlightAssociations(associations) {
            this.highlightedAssociations = [];
        }

        onHighlightGene(gene) {
            let highlightedAssociations = this.associations.filter(function(assoc:Association) {
                return gene.positions.gte <= assoc.snp.position && gene.positions.lte >= assoc.snp.position;
            });
            this.highlightedAssociations = highlightedAssociations;
        }

        onUnhighlightGene(gene) {
            this.highlightedAssociations = [];
        }
        onLoading() {
            this.loadingAsso = true;
        }
        onDrawn() {
            this.loadingAsso = false;
        }

        onLoadAssociations(associations) {
            this.associations = associations;
        }

        onHighlightAssocInTable(association: Association | null) {
            // TODO use array operators
            if (!this.loadingAsso){
                if (association == null) {
                    this.highlightedAssociations = [];
                    return;
                }
                this.highlightedAssociations = [association];
            }
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
            if(this.geneOnly == "nomac"){ // comes from study manhattan plot
                this.filters.gene = "0";
                this.filters.mac = ["0","5"];
            }
            if(this.geneOnly == "n"){ // comes from hitmap
                this.filters.gene = "0";
            }
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
                    element: ".gene-zoom",
                    intro: "You can use the zoom to show further associations linked to this gene",
                    position: "left"
                },
                {
                    element: "#manhattanplot",
                    intro: "This Manhattan plot shows all the associations that are currently displayed in the table below. Each marker in the plot is a SNP. By hovering the mouse over a marker, additional information is displayed",
                    position: "bottom"
                },
                {
                    element: "#geneplot",
                    intro: "The Gene plot aligned underneath the Manhattan plot shows the genes in the chosen region. When the user moves the mouse over a certain gene, all corresponding associations are highlighted in the Manhattan plot. If the user moves the mouse over an association in the Manhattan plot, a vertical blue line shows the location of the association in regard to the gene.",
                    position: "bottom"
                },
                {
                    element: ".associations-control-container",
                    intro: "You can use these filters to filter the top associations list and to choose the number of associations to display in the list and on the plot",
                    position: "right"
                },
                {
                    element: ".associations-table-container",
                    intro: "This table shows all top associations (sorted by score) that are stored in the database. Significant associations are marked in blue.",
                    position: "top"
                },
                {
                    element: ".associations-table-container tbody tr", //for some reason id does not work
                    intro: "To view more information about a specific association, click on the SNP link",
                    position: "bottom"
                },

            ],
            nextPage: {name: "associationDetail", params:{id: 144, assocId: "4_1267038"}}
        };
    }
</script>
<style scoped>
    .page-container {
        display:flex;
        justify-content:center;
    }
</style>
