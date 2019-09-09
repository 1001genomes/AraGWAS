<template>
    <div>
        <h3 v-if="!loaded" class="mt-4 mb-4 text-xs-center">Loading can take some time. Thank you for your patience.</h3>
        <v-progress-linear v-bind:indeterminate="true" v-if="!loaded" ></v-progress-linear>
        <svg id="heatmap" width="100%" :height="size[1]" class="mt-2" v-on:highlightassociation="onHighlightAssociation" v-on:unhighlightassociation="onUnhighlightAssociation" v-on:clicksnp="onClickAssociation" v-on:zoomin="onZoomIn" v-on:dezoom="onDezoom">
        </svg>
        <div  v-bind:style="popupStyle" id="associationpopup"  >
            <v-card v-if="highlightedPosition != 0" class="mt-1 mb-1">
                <v-card-title>
                    <dl>
                        <dt><b>Phenotype</b>: {{highlightedStudy}}</dt>
                        <dt><b>Position</b>: {{highlightedPosition}}</dt>
                        <dt><b>Score</b>: {{highlightedScore | round}}</dt>
                        <dt class="blue--text">Click to go to closest gene!</dt>
                    </dl>
                </v-card-title>
            </v-card>
        </div>
    </div>
</template>

<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import gwasheatmap from "../viz/gwasheatmap.js";

    import {loadAssociationsHeatmap,loadAssociationsHeatmapZoomed, loadAssociationsHistogram,loadAssociationsHistogramZoomed, loadGenesByRegion} from "../api";

    import _ from "lodash";

    @Component({
        name: "gwas-heatmap",
        filters: {
            round: function(value) {
                return Math.round(value * 100)/ 100;
            }
        }
    })
    export default class GwasHeatmap extends Vue {

        height:number = 800;
        width: number = 800;
        heatmap = gwasheatmap();
        debouncedOnResize = _.debounce(this.onResize, 300);
        data: Array<{}> = [];
        loaded: boolean = true;
        highlightedPosition = 0;
        highlightedScore = 0;
        highlightedStudy: string = "";

        popupStyle = {
            top: '0',
            left: '0'
        };
        pointData;
        zoomed: boolean = false;
        zoomRegion: Array<number> = [0,0,0];

        mounted() {
            this.onResize();
            this.loadData();
            window.addEventListener('resize', this.debouncedOnResize);
//            this.debouncedOnResize();
        }

        beforeDestroy() {
            window.removeEventListener('resize', this.debouncedOnResize);
        }

        get size():number[] {
            let numberOfStudies = 0;
            if ("studies" in this.data) {
             numberOfStudies = this.data['studies'].length;
            }

            let maximumheight = Math.max(this.height,numberOfStudies*11);
            return [this.width, maximumheight];
        }

        get regionWidth() {
            return 2*Math.round(30427671 / ((this.width  - 150) / 5));
        }
        get zoomRegionWidth() {
            return 2*Math.round((this.zoomRegion[2]-this.zoomRegion[1]) / ((this.width  - 150)));
        }

        onHighlightAssociation(event): void {
            this.highlightedPosition = event.detail.associations.position;
            this.highlightedScore = event.detail.associations.score;
            this.highlightedStudy = this.data['studies'][event.detail.associations.study].name;
            let e = event.detail.event;
            this.popupStyle.top = e.layerY + 10 + "px";
            this.popupStyle.left = e.layerX + "px";
        }

        onUnhighlightAssociation(event): void {
            this.highlightedPosition = 0;
        }

        onClickAssociation(event): void {
            let position = event.detail.associations[0]['pos'];
            let chromosome = event.detail.chromosome;
            // Introduce an increasing search radius
            this.loadNeighboringGenes(chromosome, position, 1000);
        }

        onZoomIn(event): void {
            this.zoomRegion = [event.detail.chromosome, event.detail.range[0], event.detail.range[1]];
            this.loadZoomedData(this.zoomRegion, this.zoomRegionWidth)
        }

        onDezoom(event): void {
            if (this.zoomed) {
                this.loadData();
            }
        }

        loadNeighboringGenes(chromosome, position, distance): void {
            loadGenesByRegion(chromosome.toString(), position-distance, position+distance, false).then( (genes) => {if (genes.length != 0) {this.$router.push({ name: 'geneDetail', params: { geneId: genes[0].name, geneOnly: "n" }})} else {this.loadNeighboringGenes(chromosome, position, 2*distance)}});
        }

        @Watch("size")
        onWidthChanged(newSize: number[], oldSize: number[]) {
            if((newSize[0]!=oldSize[0])||(newSize[1]!=oldSize[1])) {
                this.loadHistogramData();
                this.heatmap.size(newSize);
            }
        }

        onResize() {
            this.width = this.$el.offsetWidth;
            if (this.$el.parentElement) {
                this.height = this.$el.parentElement.offsetHeight;
            }
        }
        loadHistogramData() {
            this.loaded=false;
            if (!this.pointData) {
                return;
            }
            if (this.zoomed) {

                Promise.all([loadAssociationsHistogramZoomed(this.zoomRegion, this.zoomRegionWidth)])
                    .then((results) => {
                        let data = this.pointData;
                        let histogramData = results[0];
                        for (let i=0;i<histogramData['data'].length;i++) {
                            data['data'][i]['bins'] = histogramData['data'][i]['bins'];
                        }
                        this.data = data;
                        this.loaded=true;
                        d3.select("#heatmap").data([this.data]).call(this.heatmap);
                    });
            } else {
                Promise.all([loadAssociationsHistogram(this.regionWidth)])
                    .then((results) => {
                        let data = this.pointData;
                        let histogramData = results[0];
                        for (let i = 0; i < histogramData['data'].length; i++) {
                            data['data'][i]['bins'] = histogramData['data'][i]['bins'];
                        }
                        this.data = data;
                        this.loaded = true;
                        d3.select("#heatmap").data([this.data]).call(this.heatmap);
                    });
            }
        }

        loadData() {
            this.loaded=false;
            console.log('reg')
            Promise.all([loadAssociationsHeatmap(), loadAssociationsHistogram(this.regionWidth)])
                .then((results) => {
                    let data = results[0];
                    this.pointData = results[0];
                    let histogramData = results[1];
                    for (let i=0;i<histogramData['data'].length;i++) {
                        data['data'][i]['bins'] = histogramData['data'][i]['bins'];
                    }
                    this.data = data;
                    this.loaded=true;
                    d3.select("#heatmap").data([this.data]).call(this.heatmap);
                });


        }
        loadZoomedData(region, regionwidth) {
            this.loaded=false;
            Promise.all([loadAssociationsHeatmapZoomed(region,regionwidth), loadAssociationsHistogramZoomed(region,regionwidth)])
                .then((results) => {
                    let data = results[0];
                    this.pointData = results[0];
                    let histogramData = results[1];
                    for (let i=0;i<histogramData['data'].length;i++) {
                        data['data'][i]['bins'] = histogramData['data'][i]['bins'];
                    }
                    this.data = data;
                    this.loaded=true;
                    this.zoomed = true
                    d3.select("#heatmap").data([this.data]).call(this.heatmap);
                });


        }


    }
</script>
<style lang="stylus">
    #associationpopup{
        max-width:200px;
        position:absolute;
        z-index:9999;
    }

</style>
