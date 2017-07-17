<template>
    <v-layout row-xs child-flex-xs wrap justify-space-around>
        <v-flex xs3 wrap v-if="showControls.length>0 && view.controlPosition !== 'right'" class="associations-control-container">
            <div v-if="showControls.indexOf('pageSize')>-1">
                <h6 class="mt-4">Associations per page</h6>
                <v-select
                        v-bind:items="pageSizes"
                        v-model="pagination.rowsPerPage"
                        label="Associations per page"
                        light
                        single-line
                        auto
                ></v-select>
            </div>
            <div v-if="showControls.indexOf('maf')>-1">
                <h6 class="mt-4">MAF</h6>
                <v-checkbox v-model="filters.maf" primary :label="'<1% (' + roundPerc(percentage.maf['*-0.01']) + '% of associations)'" value="1" class="mb-0"></v-checkbox>
                <v-checkbox v-model="filters.maf" primary :label="'1-5% (' + roundPerc(percentage.maf['0.01-0.05']) + '% of associations)'" value="1-5" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.maf" primary :label="'5-10% (' + roundPerc(percentage.maf['0.05-0.1']) + '% of associations)'" value="5-10" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.maf" primary :label="'>10% (' + roundPerc(percentage.maf['0.1-*']) + '% of associations)'" value="10" class="mt-0"></v-checkbox>
            </div>
            <div xs column v-if="showControls.indexOf('chr')>-1">
                <h6 class="mt-4">Chromosomes</h6>
                <v-checkbox v-model="filters.chr" primary :label="'1 (' + roundPerc(percentage.chromosomes.chr1) + '% of associations)'" value="1" class="mb-0"> what</v-checkbox>
                <v-checkbox v-model="filters.chr" primary :label="'2 (' + roundPerc(percentage.chromosomes.chr2) + '% of associations)'" value="2" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.chr" primary :label="'3 (' + roundPerc(percentage.chromosomes.chr3) + '% of associations)'" value="3" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.chr" primary :label="'4 (' + roundPerc(percentage.chromosomes.chr4) + '% of associations)'" value="4" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.chr" primary :label="'5 (' + roundPerc(percentage.chromosomes.chr5) + '% of associations)'" value="5" class="mt-0"></v-checkbox>
            </div>
            <div v-if="showControls.indexOf('annotation')>-1">
                <h6 class="mt-4">Annotation</h6>
                <v-checkbox v-model="filters.annotation" primary :label="'Non-synonymous coding (' + roundPerc(percentage.annotations.ns) + '% of associations)'" value="ns" class="mb-0"></v-checkbox>
                <v-checkbox v-model="filters.annotation" primary :label="'Synonymous coding (' + roundPerc(percentage.annotations.s) + '% of associations)'" value="s" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.annotation" primary :label="'Intron (' + roundPerc(percentage.annotations.in) + '% of associations)'" value="in" class="mt-0 mb-0"></v-checkbox>
                <v-checkbox v-model="filters.annotation" primary :label="'Intergenic (' + roundPerc(percentage.annotations.i) + '% of associations)'" value="i" class="mt-0 mb-0"></v-checkbox>
            </div>
            <div v-if="showControls.indexOf('type')>-1">
                <h6 class="mt-4">Type</h6>
                <v-checkbox v-model="filters.type" primary :label="'Genic (' + roundPerc(percentage.types['1']) + '% of associations)'" value="genic" class="mb-0"></v-checkbox>
                <v-checkbox v-model="filters.type" primary :label="'Non-genic (' + roundPerc(percentage.types['0']) + '% of associations)'" value="non-genic" class="mt-0 mb-0"></v-checkbox>
            </div>
        </v-flex>
        <v-flex xs9 wrap fill-height class="association-table-container" @mouseleave="showAssociation(null)" v-show="view.controlPosition !== 'right' || showSwitch">
            <v-data-table
                    v-bind:headers="headers"
                    v-bind:items="associations"
                    v-bind:pagination.sync="pagination"
                    hide-actions
                    :loading="loading"
                    class="elevation-1 mt-2 asso-table"

            >
                <template slot="headerCell" scope="props">
                    <span v-tooltip:bottom="{ 'html': props.header.tooltip}">
                      {{ props.header.text | capitalize }}
                    </span>
                </template>
                <template slot="items" scope="props">
                    <tr :id="props.item.snp.chr + '_'+props.item.snp.position+'_' + props.item.study.id" :active="props.item.highlighted">
                        <td v-if="hideFields.indexOf('name') == -1" @mouseover="showAssociation(props.item)">
                            <div v-if="'snp' in props.item" >{{ props.item.snp.chr | capitalize }}:{{ props.item.snp.position }}</div><div v-else >Missing SNP info</div></td>
                        <td v-if="hideFields.indexOf('score') == -1" v-bind:class="['text-xs-right',{'blue--text' : props.item.overFDR}]" @mouseover="showAssociation(props.item)">{{ props.item.score | round }}</td>
                        <td v-if="hideFields.indexOf('study') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                            <router-link :to="{name: 'studyDetail', params: { id: props.item.study.id }}" >{{ props.item.study.name }}</router-link></td>
                        <td v-if="hideFields.indexOf('gene') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                            <router-link v-if="'snp' in props.item" :to="{name: 'geneDetail', params: { geneId: props.item.snp.geneName }}">{{ props.item.snp.geneName }}</router-link><div v-else class="text-xs-right">Missing SNP info</div></td>
                        <td v-if="hideFields.indexOf('maf') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">{{ props.item.maf | round }}</td>
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
        <v-flex xs11 wrap fill-height class="association-table-container" v-show="showControls.length>0 && view.controlPosition === 'right' && !showSwitch">
            <v-data-table
                    v-bind:headers="headers"
                    v-bind:items="associations"
                    v-bind:pagination.sync="pagination"
                    hide-actions
                    :loading="loading"
                    class="elevation-1 mt-2 asso-table"
            >
                <template slot="headerCell" scope="props">
                    <span v-tooltip:bottom="{ 'html': props.header.tooltip}">
                      {{ props.header.text | capitalize }}
                    </span>
                </template>
                <template slot="items" scope="props" @mouseover.native="showAssociation">
                    <tr :id="props.item.snp.chr + '_'+props.item.snp.position+'_' + props.item.study.id" :active="props.item.highlighted">
                        <td v-if="hideFields.indexOf('name') == -1" @mouseover="showAssociation(props.item)">
                            <div v-if="'snp' in props.item" >{{ props.item.snp.chr | capitalize }}:{{ props.item.snp.position }}</div><div v-else >Missing SNP info</div></td>
                        <td v-if="hideFields.indexOf('score') == -1" v-bind:class="['text-xs-right',{'blue--text' : props.item.overFDR}]" @mouseover="showAssociation(props.item)">{{ props.item.score | round }}</td>
                        <td v-if="hideFields.indexOf('study') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                            <router-link :to="{name: 'studyDetail', params: { id: props.item.study.id }}" >{{ props.item.study.name }}</router-link></td>
                        <td v-if="hideFields.indexOf('gene') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">
                            <router-link v-if="'snp' in props.item" :to="{name: 'geneDetail', params: { geneId: props.item.snp.geneName }}">{{ props.item.snp.geneName }}</router-link><div v-else class="text-xs-right">Missing SNP info</div></td>
                        <td v-if="hideFields.indexOf('maf') == -1" class="text-xs-right" @mouseover="showAssociation(props.item)">{{ props.item.maf | round }}</td>
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
        </v-flex>
        <v-flex xs3 row v-show="showSwitch">
            <v-layout row>
                <v-flex xs10 wrap v-if="showControls.length>0 && view.controlPosition === 'right' && showSwitch" class="associations-control-container">
                    <div v-if="showControls.indexOf('maf')>-1">
                        <h6 class="mt-4">MAF</h6>
                        <v-checkbox v-model="filters.maf" primary :label="'<1% (' + roundPerc(percentage.maf['*-0.01']) + '% of associations)'" value="1" class="mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.maf" primary :label="'1-5% (' + roundPerc(percentage.maf['0.01-0.05']) + '% of associations)'" value="1-5" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.maf" primary :label="'5-10% (' + roundPerc(percentage.maf['0.05-0.1']) + '% of associations)'" value="5-10" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.maf" primary :label="'>10% (' + roundPerc(percentage.maf['0.1-*']) + '% of associations)'" value="10" class="mt-0"></v-checkbox>
                    </div>
                    <div xs column v-if="showControls.indexOf('chr')>-1">
                        <h6 class="mt-4">Chromosomes</h6>
                        <v-checkbox v-model="filters.chr" primary :label="'1 (' + roundPerc(percentage.chromosomes.chr1) + '% of associations)'" value="1" class="mb-0"> what</v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'2 (' + roundPerc(percentage.chromosomes.chr2) + '% of associations)'" value="2" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'3 (' + roundPerc(percentage.chromosomes.chr3) + '% of associations)'" value="3" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'4 (' + roundPerc(percentage.chromosomes.chr4) + '% of associations)'" value="4" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.chr" primary :label="'5 (' + roundPerc(percentage.chromosomes.chr5) + '% of associations)'" value="5" class="mt-0"></v-checkbox>
                    </div>
                    <div v-if="showControls.indexOf('annotation')>-1">
                        <h6 class="mt-4">Annotation</h6>
                        <v-checkbox v-model="filters.annotation" primary :label="'Non-synonymous coding (' + roundPerc(percentage.annotations.ns) + '% of associations)'" value="ns" class="mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.annotation" primary :label="'Synonymous coding (' + roundPerc(percentage.annotations.s) + '% of associations)'" value="s" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.annotation" primary :label="'Intron (' + roundPerc(percentage.annotations.in) + '% of associations)'" value="in" class="mt-0 mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.annotation" primary :label="'Intergenic (' + roundPerc(percentage.annotations.i) + '% of associations)'" value="i" class="mt-0 mb-0"></v-checkbox>
                    </div>
                    <div v-if="showControls.indexOf('type')>-1">
                        <h6 class="mt-4">Type</h6>
                        <v-checkbox v-model="filters.type" primary :label="'Genic (' + roundPerc(percentage.types['1']) + '% of associations)'" value="genic" class="mb-0"></v-checkbox>
                        <v-checkbox v-model="filters.type" primary :label="'Non-genic (' + roundPerc(percentage.types['0']) + '% of associations)'" value="non-genic" class="mt-0 mb-0"></v-checkbox>
                    </div>
            </v-flex>
            <v-flex xs2 class="text-xs-right">
                <br>
                <br>
                <br>
                <p class="text-xs-right"><v-switch v-model="showSwitch" primary label="Controls" class="mb-0 switch"></v-switch></p>
            </v-flex>
            </v-layout>
        </v-flex>
        <v-flex xs1 v-show="showControls.length>0 && view.controlPosition === 'right' && !showSwitch" class="text-xs-right">
            <v-layout>
                <v-flex xs6 offset-xs6>
                    <br>
                    <br>
                    <br>
                    <p class="text-xs-right"><v-switch v-model="showSwitch" primary label="Controls" class="mb-0 switch"></v-switch></p>
                </v-flex>
            </v-layout>
        </v-flex>
    </v-layout>
</template>


<script lang="ts">
    import Vue from "vue";
    import {Component, Watch, Prop} from "vue-property-decorator";
    import Association from "../models/association"

    import {loadTopAssociations, loadAssociationsOfPhenotype, loadAssociationsOfStudy, loadAssociationsOfGene, loadSnpStatistics, loadAggregatedStatisticsOfGene, loadAggregatedStatisticsOfPhenotype, loadAggregatedStatisticsOfStudy, loadTopAggregatedStatistics} from "../api";

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
        view: {name: "top-associations", phenotypeId: 0, studyId: 0, geneId: "1", zoom: 0, controlPosition: "left"};
        @Prop()
        filters: {chr: string[], annotation: string[], maf: string[], type: string[]};
        @Prop({type: null})
        highlightedAssociations: Association[];
        localfilters : {};
        loading: boolean = false;
        headers = [{text: "SNP", value: "snp.chr", name: "name", align: "left", tooltip: "Name of SNP"},{text: "score", value: "score", name: "score", tooltip: "-log10(p-value)"},
            {text: "study", value: "study.name", name: "study", sortable: false, tooltip: "Study"},{text: "gene",value: "snp.geneName", name: "gene", sortable: false, tooltip: "Gene"},
            {text: "maf",value: "maf", name: "maf", sortable: false, tooltip: "Minor Allele Frequency"},{text: "phenotype",value: "study.phenotype.name", name: "phenotype", sortable: false, tooltip: "Phenotype"},
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
        showSwitch = false;
        lastElement: [number, string];
        lastElementHistory = {'1': [0,''], };
        percentage = {chromosomes: {}, annotations: {}, types: {}, maf: {}};
        debouncedloadData = _.debounce(this.loadData, 300);
        selected = [];
        pageSizes = [25, 50, 75, 100, 200,];


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
            this.associations = data.results;
            this.pagination.totalItems = data.count;
            this.pageCount = Math.ceil(data.count/this.pagination.rowsPerPage);
            this.loading = false;
            this.lastElement = data.lastel;
            this.$emit('load', this.associations);;
        }
        hideHeaders(fields): void {
            for(let i = this.headers.length-1; i>= 0; i--) {
                if (fields.indexOf(this.headers[i].name)>-1){
                    this.headers.splice(i,1)
                }
            }
        }
        showAssociation(item): void {
            this.$emit('association', item)
        }
        percentageString(el: number): string {
            const outstr = " (" + Math.round(1000*el)/10 + "% of associations)";
            return outstr
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

    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .page-container {
        display:flex;
        justify-content:center;
    }
    .asso-table th {
        text-align: left !important;
    }
    .switch {
        transform: rotate(270deg);
    }

    .asso-table tr[active] {
        background-color:#FFEB3B;
    }

</style>
