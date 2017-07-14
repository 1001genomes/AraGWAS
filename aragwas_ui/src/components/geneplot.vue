<template>
    <div style="position:relative">
        <svg id="manhattanplot" :height="scatterPlotHeight" width="100%" v-on:highlightassociations="onHighlightAssociations" v-on:unhighlightassociations="onUnhighlightAssociations" >
        </svg>
        <svg id="geneplot" width="100%" :height="genePlotHeight" :style="genePlotStyles" v-on:highlightgene="onHighlightGene" v-on:unhighlightgene="onUnhighlightGene" >
        </svg>
        <div class="colorlegend-container">
            <v-select
                :items="colorLegendTypes"
                v-model="activeColorLegend"
                label="Color"
                single-line
                item-value="name"
                left
                return-object
            ></v-select>
        </div>
        <div  v-bind:style="popupStyle" id="genepopup"  >
            <v-card v-if="highlightedGene != null" >
                <v-card-row class="green darken-1">
                    <v-card-title>
                        <span class="white--text">{{highlightedGene.name}}</span>
                        <v-spacer></v-spacer>
                    </v-card-title>
                </v-card-row>
                <v-card-text>
                    <v-card-row>
                        Position: {{highlightedGene.originalStart}} - {{highlightedGene.originalEnd}}
                    </v-card-row>
                    <v-card-row>
                        Description: {{highlightedGene.description}}
                    </v-card-row>
                </v-card-text>
            </v-card>
        </div>
        <div id="associationpopup" v-if="highlightedAssociation">
            <dl>
                <dt></dt><dd>{{highlightedAssociation.snp.position}}</dd>
                <dt class="pvalue">-log10(pvalue):</dt><dd>{{highlightedAssociation.score | round}}</dd>
            </dl>
        </div>
    </div>
</template>

<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import Association from "../models/association"
    import Gene, {GenePlotOptions} from "../models/gene";

    import geneplot from "../viz/geneplot.js";
    import manhattanplot from "../viz/manhattanplot.js";

    import _ from "lodash";

    @Component({
        name: "gene-plot",
        filters: {
            round: function(value) {
                return Math.round(value * 100)/ 100;
            }
        }
    })
    export default class GenePlot extends Vue {
        @Prop({type:null})
        associations;

        @Prop({type: null})
        highlightedAssociations: Association[];

        @Prop()
        genes: Gene[];

        @Prop()
        options: GenePlotOptions;


        width: number = 0;
        scatterPlotHeight: number = 300;
        genePlotHeight: number = 250;
        readonly alpha: number = 0.05;
        readonly padding = 40;
        scales = {x: d3.scaleLinear(), y: d3.scaleLinear()};
        axis = {x: d3.axisBottom(this.scales.x), y: d3.axisLeft(this.scales.y)};
        genePlt = geneplot();
        manhattanPlt = manhattanplot();
        debouncedOnResize = _.debounce(this.onResize, 300);

        debouncedDrawGenePlot = _.debounce(this.drawGenePlot, 300);
        debouncedDrawManhattanPlot = _.debounce(this.drawManhattanPlot, 300);
        popupPosX = 0;
        threshold = 8.0;

        popupStyle = {
            top: '0',
            left: '0'
        }
        popupPosY = 0;
        activeColor= "red";
        fontSize = 30;

        highlightedGene: Gene | null = null;
        readonly colorLegendTypes = [{text: "Same color", name: "", isNumber: true}, {text: "Impact", name: "snp.annotations.0.impact", isNumber: false}, {text: "MAF", name: "maf", isNumber:true}, {text: "MAC", name: "mac", isNumber:true}, {text: "Score", name: "score", isNumber:true}];
        activeColorLegend = this.colorLegendTypes[1];

        readonly margin = {
            left: 60,
            right: 50,
            bottom: 0,
            top: 0,
        }

        onHighlightGene(event): void {
            let gene = event.detail.gene;
            this.highlightedGene = gene;
            let e = event.detail.event;
            this.popupStyle.top = e.pageY + 10 + "px";
            this.popupStyle.left = e.pageX + "px";
            // not necessariy because prop will be updated. If this is enabled than it should be de-bounced
            /*this.manhattanPlt.highlightSnps(this.associations.filter(function(assoc) {
                return assoc.snp.position >= gene.positions.gte && assoc.snp.position <= gene.positions.lte;
            }));*/
            this.$emit("highlightgene", event.detail.gene);

       }

        onUnhighlightGene(event): void {
            this.highlightedGene = null;
            // not necessariy because prop will be updated. If this is enabled than it should be de-bounced
            // this.manhattanPlt.highlightSnps([]);
            this.$emit("unhighlightgene", []);
        }

        onHighlightAssociations(event): void {
            var associations = event.detail.associations;
            this.genePlt.highlightPos(associations[0].snp.position);
            this.$emit("highlightassociations", associations);
        }

        onUnhighlightAssociations(event): void {
            this.genePlt.highlightPos([]);
            this.$emit("unhighlightassociations", []);
        }

        get height() {
            return this.scatterPlotHeight + this.genePlotHeight;
        }

        get genePlotStyles() {
            return {
                "margin-left": this.margin.left + 'px',
                "margin-right": this.margin.right + 'px',
                "margin-top": this.margin.top + 'px',
                "margin-bottom": this.margin.bottom + 'px',
            };
        }

        get isoforms() {
            const isoforms = [];
            this.genes.forEach(function(d) {
                isoforms.push.apply(isoforms, d['isoforms']);
            });
            return isoforms;
        }

        get highlightedAssociation() {
            if (! (this.highlightedAssociations) || this.highlightedAssociations.length > 1) {
                return null;
            }
            return this.highlightedAssociations[0];
        }

        @Watch("width")
        onWidthChanged(newWidth: number, oldWidth: number) {
            this.genePlt.size([newWidth - this.margin.left - this.margin.right - this.manhattanPlt.sideSettingsWidth(), this.genePlotHeight]);
            this.manhattanPlt.size([newWidth, this.scatterPlotHeight]);
        }

        @Watch("options")
        onOptionsChanged(newOptions: GenePlotOptions, oldOptions: GenePlotOptions) {
            this.genePlt.region([newOptions.startPos,newOptions.endPos]);
            this.manhattanPlt.region([newOptions.startPos,newOptions.endPos]);
            this.manhattanPlt.threshold(newOptions.bonferoniThreshold);
            this.debouncedDrawGenePlot();
            this.debouncedDrawManhattanPlot();
        }

        @Watch("activeColorLegend")
        onActiveColorLegendChanged(newActiveColorLegend) {
            this.manhattanPlt.activeColorLegend(newActiveColorLegend);
        }


        @Watch("isoforms")
        onGenesChanged() {
            this.debouncedDrawGenePlot();
        }


        @Watch("associations")
        onAssociationsChanged(newAssociations) {
            this.debouncedDrawManhattanPlot();
        }
        @Watch("highlightedAssociations")
        onHighlightedAssociationsChanged(newHighlightedAssociations) {
            if (!newHighlightedAssociations || newHighlightedAssociations.length === 0) {
                this.genePlt.highlightPos(undefined);
                this.manhattanPlt.highlightAssociations([]);
            }
            else {
                let highlightedAssociation = newHighlightedAssociations[0];
                let position = highlightedAssociation.snp.position;
                this.genePlt.highlightPos(position);
                this.manhattanPlt.highlightAssociations(newHighlightedAssociations);
            }
        }

        mounted() {
            this.genePlt.region([this.options.startPos,this.options.endPos]);
            this.manhattanPlt.region([this.options.startPos,this.options.endPos]).threshold(this.threshold).showXAxis(false).activeColorLegend(this.activeColorLegend);
            d3.select("#geneplot").data([this.isoforms]).call(this.genePlt);
            d3.select("#manhattanplot").data([this.associations]).call(this.manhattanPlt);
            window.addEventListener('resize', this.debouncedOnResize);
            this.debouncedOnResize();
        }

        beforeDestroy() {
            window.removeEventListener('resize', this.debouncedOnResize);
        }

        onResize() {
            this.width = this.$el.offsetWidth;
        }

        drawManhattanPlot() {
            this.manhattanPlt.data(this.associations);
        }

        drawGenePlot() {
            this.genePlt.data(this.isoforms);
        }

    }
</script>
<style lang="stylus">
    highlight-color = #007EFF;highlightedGene
    svg#geneplot
        g.isoform
            rect.gene
                fill: #687a97;
        g.isoform.highlight
            text
                fill: highlight-color;
            rect.gene
                fill: highlight-color;
            rect.highlight
                stroke:highlight-color;


    #genepopup
        max-width:400px;
        position:absolute;
        z-index:9999;

    #associationpopup
        position: absolute;
        z-index: 9999;
        top:0px;
        right: 20px;
        dt.pvalue
            color:green;
        dd
            float:left;
            margin-right: 10px;
        dt
            float:left;
            margin-right:2px;

    .colorlegend-container
        position:absolute;
        top:0;
        right:0;
        z-index:2;
        width:115px;
        height:52px;


</style>
