<template>
    <v-layout wrap column justify-space-around v-bind:class="{'right-controls':view.controlPosition}">
        <div class="switch-container">
            <v-switch v-model="showFilters" primary hide-details label="Show filters" class="mb-0"></v-switch>
        </div>
        <v-flex>
            <v-layout v-bind="layoutBinding">
                <div v-bind:open="showFilters" class="pr-1 pl-1 associations-control-container">
                    <div v-if="showControls.indexOf('pageSize')>-1">
                        <h6 class="mt-4">Associations per page</h6>
                        <v-select
                                v-bind:items="pageSizes"
                                v-model="pagination.rowsPerPage"
                                label="Associations per page"
                                light
                                single-line
                                auto hide-details
                        ></v-select>
                    </div>
                    <div v-if="showControls.indexOf('significant')>-1">
                        <h6 class="mt-4">Significance</h6>
                        <v-switch
                                label="Only show significant hits"
                                v-model="significant"
                                primary
                                class="mt-0 mb-0 pt-0" hide-details
                        ></v-switch>
                        <div class="ml-3" v-if="significant">
                            <v-radio-group v-model="filters.significant" >
                                <v-radio label="Permutation threshold" value="p" ></v-radio>
                                <v-radio label="Bonferroni threshold"  value="b" ></v-radio>
                            </v-radio-group>
                        </div>
                        <div>If turned off, all associations with p-value < 10<sup>-4</sup> will be displayed.</div>
                    </div>
                    <div v-if="showControls.indexOf('geneonly')>-1">
                        <h6 class="mt-4">Gene options</h6>
                        <v-switch
                                label="Only show SNPs for selected gene"
                                v-model="showOnlySelectedGene"
                                primary
                                class="mt-0 mb-0 pt-0" hide-details
                        ></v-switch>
                        <div>If turned off, all associations in the area covered by the zoom will be displayed.</div>
                    </div>
                    <div v-if="showControls.indexOf('maf')>-1">
                        <h6 class="mt-4">MAF</h6>
                        <v-checkbox v-model="filters.maf" primary :label="'<1% (' + roundPerc(percentage.maf['*-0.01']) + '% of associations)'" value="1"  class="pt-0" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.maf" primary :label="'1-5% (' + roundPerc(percentage.maf['0.01-0.05001']) + '% of associations)'" value="1-5"  hide-details></v-checkbox>
                        <v-checkbox v-model="filters.maf" primary :label="'5-10% (' + roundPerc(percentage.maf['0.05001-0.1001']) + '% of associations)'" value="5-10" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.maf" primary :label="'>10% (' + roundPerc(percentage.maf['0.1001-*']) + '% of associations)'" value="10"  hide-details></v-checkbox>
                    </div>
                    <div v-if="showControls.indexOf('mac')>-1">
                        <h6 class="mt-5">MAC</h6>
                        <v-checkbox v-model="filters.mac" primary :label="'≤5 (' + roundPerc(percentage.mac['*-6.0']) + '% of associations)'" value="0" class="pt-0" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.mac" primary :label="'>5 (' + roundPerc(percentage.mac['6.0-*']) + '% of associations)'" value="5" hide-details></v-checkbox>
                    </div>
                    <div xs column v-if="showControls.indexOf('chr')>-1">
                        <h6 class="mt-5">Chromosomes</h6>
                        <v-checkbox v-model="filters.chr" primary :label="'1 (' + roundPerc(percentage.chromosomes.chr1) + '% of associations)'" value="1" class="pt-0" hide-details> what</v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'2 (' + roundPerc(percentage.chromosomes.chr2) + '% of associations)'" value="2" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'3 (' + roundPerc(percentage.chromosomes.chr3) + '% of associations)'" value="3" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'4 (' + roundPerc(percentage.chromosomes.chr4) + '% of associations)'" value="4" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'5 (' + roundPerc(percentage.chromosomes.chr5) + '% of associations)'" value="5" hide-details></v-checkbox>
                    </div>
                    <div v-if="showControls.indexOf('annotation')>-1">
                        <h6 class="mt-5">Annotation</h6>
                        <v-checkbox v-model="filters.annotation" primary :label="'Non-synonymous coding (' + roundPerc(percentage.annotations.ns) + '% of associations)'" class="pt-0" value="ns" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.annotation" primary :label="'Synonymous coding (' + roundPerc(percentage.annotations.s) + '% of associations)'" value="s" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.annotation" primary :label="'Intron (' + roundPerc(percentage.annotations.in) + '% of associations)'" value="in" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.annotation" primary :label="'Intergenic (' + roundPerc(percentage.annotations.i) + '% of associations)'" value="i" hide-details></v-checkbox>
                    </div>
                    <div v-if="showControls.indexOf('type')>-1">
                        <h6 class="mt-5">Type</h6>
                        <v-checkbox v-model="filters.type" primary :label="'Genic (' + roundPerc(percentage.types['1']) + '% of associations)'" value="genic" class="pt-0" hide-details></v-checkbox>
                        <v-checkbox v-model="filters.type" primary :label="'Non-genic (' + roundPerc(percentage.types['0']) + '% of associations)'" value="non-genic" hide-details></v-checkbox>
                    </div>
                    <div class="text-xs-center mb-3">
                        <h6 class="mt-5">Download</h6>
                        <div class="grey--text">Download the filtered associations (since the file first needs to be generated, this may take a while, please only click once)</div>
                        <v-btn floating primary class="mr-3 mt-2 btn--large" tag="a" :href="_getDownloadHref()" download v-tooltip:bottom="{html: 'Download set of filtered associations'}">
                            <v-icon dark>file_download</v-icon>
                        </v-btn>
                    </div>
                </div>
                <v-flex wrap fill-height class="pl-1 pr-1 associations-table-container" >
                    <v-data-table
                            v-bind:headers="headers"
                            v-bind:items="associations"
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
                            <tr :id="('snp' in props.item)? props.item.snp.chr + '_'+props.item.snp.position+'_' + props.item.study.id : 'missing_info'" >
                                <td v-if="hideFields.indexOf('name') == -1" @mouseover="showAssociation(props.item)">
                                    <div v-if="'snp' in props.item" ><router-link v-if="'snp' in props.item" :to="{name: 'associationDetail', params: { id: props.item.study.id, assocId: props.item.snp.chr.slice(-1) + '_'+props.item.snp.position }}">{{ props.item.snp.chr | capitalize }}:{{ props.item.snp.position }}</router-link></div><div v-else >Missing SNP info</div></td>
                                <td v-if="hideFields.indexOf('score') == -1" v-bind:class="['text-xs-right',{'blue--text' : props.item.overPermutation}]" @mouseover="showAssociation(props.item)">{{ props.item.score | round }}</td>
                                <td v-if="hideFields.indexOf('study') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                                    <router-link :to="{name: 'studyDetail', params: { id: props.item.study.id }}" >{{ props.item.study.phenotype.name }}</router-link></td>
                                <td v-if="hideFields.indexOf('gene') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                                    <router-link v-if="'snp' in props.item" :to="{name: 'geneDetail', params: { geneId: props.item.snp.geneName }}">{{ props.item.snp.geneName }}</router-link><div v-else class="text-xs-right">Missing SNP info</div></td>
                                <td v-if="hideFields.indexOf('maf') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">{{ props.item.maf | round }}</td>
                                <td v-if="hideFields.indexOf('mac') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">{{ props.item.mac }}</td>
                                <td v-if="hideFields.indexOf('phenotype') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                                    <router-link :to="{name: 'phenotypeDetail', params: { id: props.item.study.phenotype.id }}">{{ props.item.study.phenotype.name }}</router-link></td>
                                <td v-if="hideFields.indexOf('annotation') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                                    <div v-if="'snp' in props.item">
                                        <span v-if="props.item.snp.annotations.length > 0 ">{{ props.item.snp.annotations[0].effect | toLowerCap }}</span>
                                    </div>
                                    <div v-else>Missing SNP info</div>
                                </td>
                                <td v-if="hideFields.indexOf('type') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                                    <div v-if="'snp' in props.item">
                                        <span v-if="props.item.snp.coding">Genic</span><span v-else>Non-genic</span>
                                    </div>
                                    <div v-else>Missing SNP info</div>
                                </td>
                            </tr>
                        </template>
                    </v-data-table>
                    <div class="page-container mt-5 mb-3">
                        <v-pagination :length="pageCount" v-model="currentPage"  v-if="view.name !== 'top-associations'">
                        </v-pagination>
                        <div v-else>
                            <v-btn floating secondary @click="previous" :disabled="pager===1"><v-icon light>keyboard_arrow_left</v-icon></v-btn>
                            <v-btn floating secondary @click="next" :disabled="pager===pageCount"><v-icon light>keyboard_arrow_right</v-icon></v-btn>
                        </div>
                    </div>
                </v-flex >
            </v-layout>
        </v-flex>
    </v-layout>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch, Prop} from "vue-property-decorator";
    import Association from "../models/association"

    import {loadTopAssociations, loadAssociationsOfPhenotype, loadAssociationsOfStudy, loadAssociationsOfGene,
        loadSnpStatistics, loadAggregatedStatisticsOfGene, loadAggregatedStatisticsOfPhenotype,
        loadAggregatedStatisticsOfStudy, loadTopAggregatedStatistics, getTopAssociationsParametersQuery} from "../api";

    import _ from "lodash";

    @Component({
        filters: {
            capitalize(str) {
                return str.charAt(0).toUpperCase() + str.slice(1);
            },
            toLowerCap(str) {
                return (str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()).split("_").join(" ");
            },
            round(number) {
                return Math.round(number * 1000) / 1000;
            },
            roundPerc(number) {
                return Math.round(number * 1000) / 10;
            },
        },
        name: "topAssociations",
        props: ["showControls", "hideFields", "filters", "view", "highlightedAssociations"],
    })
    export default class TopAssociationsComponent extends Vue {
        @Prop()
        showControls: string[];
        @Prop()
        hideFields: string[];
        @Prop()
        view: {name: "top-associations", phenotypeId: 0, studyId: 0, geneId: "1", zoom: 0, controlPosition: "left", filtersOpen: true};
        @Prop()
        filters: {chr: string[], annotation: string[], maf: string[], mac: string[], type: string[], significant: string, gene: string};
        @Prop({type: null})
        highlightedAssociations: Association[];
        localfilters : {};
        loading: boolean = false;
        noDataText: string = "No data available.";
        headers = [{text: "SNP", value: "snp.chr", name: "name", align: "left", tooltip: "Name of SNP"},{text: "score", value: "score", name: "score", tooltip: "-log10(p-value)"},
            {text: "study", value: "study.name", name: "study", sortable: false, tooltip: "Study"},{text: "gene",value: "snp.geneName", name: "gene", sortable: false, tooltip: "Gene"},
            {text: "MAF",value: "maf", name: "maf", sortable: false, tooltip: "Minor Allele Frequency"},{text: "MAC",value: "mac", name: "mac", sortable: false, tooltip: "Minor Allele Count"},
            {text: "phenotype",value: "study.phenotype.name", name: "phenotype", sortable: false, tooltip: "Phenotype"},
            {text: "annotation",value: "annotation", name: "annotation", sortable: false, tooltip: "Annotation related to associated SNP"},{text: "type",value: "snp.type", name: "type", sortable: false, tooltip: "Type of SNP"}];
        associations: Association[] =[];
        currentPage = 1;
        pager = 1;
        pageCount = 5;
        totalCount = 0;
        breadcrumbs = [{text: "Home", href: "/"}, {text: "Top Associations", href: "#/top-associations", disabled: true}];
        maf = ["1", "1-5", "5-10", "10"];
        chr = ["1", "2", "3", "4", "5"];
        annotation = ["ns", "s", "in", "i"];
        type = ["genic", "non-genic"];
        pagination = {rowsPerPage: 25, totalItems: 0, page: 1, ordering: name, sortBy: "score", descending: true};
        showFilters = false;
        lastElement: [number, string];
        lastElementHistory = {'1': [0,''], };
        percentage = {chromosomes: {}, annotations: {}, types: {}, maf: {}, mac: {}};
        debouncedloadDataTrue = _.debounce(this.loadData, 300);
        selected = [];
        pageSizes = [25, 50, 75, 100, 200,];
        significant = this.filters.significant !== "0";
        showOnlySelectedGene = this.filters.gene != "0";
        readonly showFilterWidth = 1090;

        debouncedloadData(a):void {
            this.$emit('loading'); //send it here to avoid the debounce time.
            this.debouncedloadDataTrue(this.currentPage)
        }

        @Watch("$vuetify.breakpoint")
        onBreakPointChanged() {
            this.showFilters = this.$el.offsetWidth >= this.showFilterWidth;
        }

        @Watch("currentPage")
        onCurrentPageChanged(val: number, oldVal: number) {
            this.$emit('loading'); //send it here to avoid the debounce time.
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.maf")
        onMafChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.mac")
        onMacChanged(val: number, oldVal: number) {
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
        @Watch("filters.significant")
        onSignificantChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("filters.gene")
        onSelectedChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("significant")
        onSigChanged(val: boolean, oldVal: boolean) {
            if(val){
                this.filters.significant = "p";
            }
            else {
                this.filters.significant = "0";
            }
        }
        @Watch("showOnlySelectedGene")
        onSelChanged(val: boolean, oldVal: boolean) {
            console.log("true");
            if(val){
                console.log("true");
                this.filters.gene = "1";
            }
            else {
                console.log("false");
                this.filters.gene = "0";
            }
        }

        @Watch("view.zoom")
        onZoomChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("view.phenotypeId")
        onPhenotypeIdChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("view.studyId")
        onStudyIdChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("view.geneId")
        onGeneIdChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("pagination.rowsPerPage")
        onRowsPerPageChanged(val: number, oldVal: number) {
            this.debouncedloadData(this.currentPage);
        }
        @Watch("highlightedAssociations")
        onHighlightedAssociationsChanged(newHighlightedAssociations) {
            this.searchForAsso(newHighlightedAssociations);
        }

        mounted(): void {
            this.showFilters = this.$el.offsetWidth >= this.showFilterWidth;
            this.hideHeaders(this.hideFields);
            this.loadData(this.currentPage);
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
            if (this.view.name == "top-associations") {
                // Need to check for already visited pages
                loadTopAssociations(this.filters, pageToLoad, this.lastElementHistory[pageToLoad.toString()]).then(this._displayData);
                loadTopAggregatedStatistics(this.filters).then(this._displayAggregatedData);
                this.pager = pageToLoad;
            } else if (this.view.name == "phenotype") {
                loadAssociationsOfPhenotype(this.view.phenotypeId, this.filters, pageToLoad).then(this._displayData);
                loadAggregatedStatisticsOfPhenotype(this.view.phenotypeId, this.filters).then(this._displayAggregatedData);
            } else if (this.view.name == "study") {
                loadAssociationsOfStudy(this.view.studyId, this.filters, pageToLoad).then(this._displayData);
                loadAggregatedStatisticsOfStudy(this.view.studyId, this.filters).then(this._displayAggregatedData);
            } else if (this.view.name == "gene") {
                loadAssociationsOfGene(this.view.geneId, this.view.zoom, this.filters, pageToLoad, this.pagination.rowsPerPage).then(this._displayData);
                loadAggregatedStatisticsOfGene(this.view.geneId, this.view.zoom, this.filters).then(this._displayAggregatedData);
            }
        }
        _displayAggregatedData(data): void {
            this.percentage = data;

        }
        _displayData(data): void {
            // Check if list is empty (in case reload data from first page)
            if(data.results.length == 0 && this.currentPage != 1){
                this.currentPage = 1;
                this.debouncedloadData(this.currentPage);
                return
            }
            this.associations = data.results;
            this.pagination.totalItems = data.count;
            this.pageCount = Math.ceil(data.count/this.pagination.rowsPerPage);
            this.loading = false;
            this.noDataText = "No data available.";
            this.lastElement = data.lastel;
            this.$emit('loaded', this.associations);
        }
        hideHeaders(fields): void {
            for(let i = this.headers.length-1; i>= 0; i--) {
                if (fields.indexOf(this.headers[i].name)>-1){
                    this.headers.splice(i,1)
                }
            }
        }
        showAssociation(item): void {
            this.$emit('association', item) // this event will be blocked by geneDetail if the associations are not drawn on manhattanplot.js
        }

        roundPerc(number): number {
            if (isNaN(number)) {
                return 0.0
            }
            return Math.round(number * 1000) / 10;
        }
        searchForAsso(associations: Association[]) {
            [].forEach.call(this.$el.querySelectorAll(".asso-table tr[active]"), function(vl, i) {
                vl.removeAttribute("active");
            });
            for (let i=0;i< associations.length;i++) {
                let association = associations[i];
                let associationId = this._getAssociationId(association);
                [].forEach.call(this.$el.querySelectorAll(".asso-table tr#" + associationId), function(vl, i) {
                    vl.setAttribute("active", "");
                });
            }
        }
        _getAssociationId(association: Association): string {
            return association.snp.chr + "_" + association.snp.position + "_" + association.study.id;
        }
        _getDownloadHref(): string {
            let url = "/api/associations/download/?"+getTopAssociationsParametersQuery(this.filters);
            if (this.view.name == "top-associations") {
            } else if (this.view.name == "phenotype") {
                url = url + "&phenotype_id="+this.view.phenotypeId;
            } else if (this.view.name == "study") {
                url = url + "&study_id="+this.view.studyId;
            } else if (this.view.name == "gene") {
                url = url + "&gene_id="+this.view.geneId+"&zoom="+this.view.zoom;
            }
            return url
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
<style>
table.table tbody tr[active] {
        background-color:#FFEB3B !important;
}
</style>
<style scoped>
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

    .right-controls div.switch-container {
        margin-left: auto;
        width:131px;
    }

    .right-controls .row .associations-control-container {
        -webkit-box-ordinal-group: 3;
        -ms-flex-order: 2;
        order: 2;
    }
    .right-controls .row .associations-table-container {
        -webkit-box-ordinal-group: 2;
        -ms-flex-order: 1;
        order: 1;
    }

</style>
