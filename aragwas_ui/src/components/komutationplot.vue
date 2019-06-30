<template>
    <div>
        <svg :id="'komutationplot'+options.chr.toString()" :height="plotHeight" width="100%" class="manhattan" v-on:highlightassociation="onHighlightAssociation" v-on:unhighlightassociation="onUnhighlightAssociation" v-on:clicksnp="onClickAssociation">
        </svg>
        <div  v-bind:style="popupStyle" id="koassociationpopup"  >
            <v-card v-if="highlightedAssociation != null" class="mt-1 mb-1">
                <v-card-title>
                    <dl>
                        <dt><b>Gene</b>: {{highlightedAssociation[0][3]}}</dt>
                        <dt><b>Position</b>: {{highlightedAssociation[0][0]}}</dt>
                        <dt><b>Score</b>: {{highlightedAssociation[0][1] | round}}</dt>
                        <dt><b>MAF</b>: {{highlightedAssociation[0][2] | round}}</dt>
                        <dt class="blue--text">Click to go to gene, more info is there!</dt>
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

    import Association from "../models/association"
    import Gene, {ManhattanPlotOptions} from "../models/study";

    import geneplot from "../viz/geneplot.js";
    import manhattanplotfullchromosome from "../viz/manhattanplotfullchromosome.js";
    import {loadGenesByRegion} from "../api";

    import _ from "lodash";
    import Router from "../router";

    @Component({
        name: "ko-mutation-plot",
        props: ["dataPoints", "options", "shown"],
        filters: {
            round(number) {
                return Math.round(number * 1000) / 1000;
            },
        }
    })
    export default class KOMutationPlot extends Vue {
        @Prop()
        dataPoints;

        @Prop()
        options: ManhattanPlotOptions;

        @Prop()
        shown;

        width: number = 0;
        plotHeight: number = 300;
        readonly alpha: number = 0.05;
        readonly padding = 40;

        highlightedAssociation: Object | null = null;
        genes: Gene[] = [];

        scales = {x: d3.scaleLinear(), y: d3.scaleLinear()};
        axis = {x: d3.axisBottom(this.scales.x), y: d3.axisLeft(this.scales.y)};
        manhattanPlt = manhattanplotfullchromosome();
        debouncedOnResize = _.debounce(this.onResize, 300);
        debouncedDrawManhattanPlot = _.debounce(this.drawManhattanPlot, 300);


        popupStyle = {
            top: '0',
            left: '0'
        };

        firstResize = false;

        get height() {
            return this.plotHeight;
        }

        onHighlightAssociation(event): void {
            this.highlightedAssociation = event.detail.associations;
            let e = event.detail.event;
            this.popupStyle.top = e.layerY + 10 + "px";
            this.popupStyle.left = e.layerX + "px";
        }

        onUnhighlightAssociation(event): void {
            this.highlightedAssociation = null;
        }

        onClickAssociation(event): void {
            // Go to gene of interest
            this.$router.push({ name: 'geneDetail', params: { geneId: event.detail.associations[0][3], geneOnly: "nomac" }})
        }

        @Watch("width")
        onWidthChanged(newWidth: number, oldWidth: number) {
            this.manhattanPlt.clear();
            this.manhattanPlt.size([newWidth, this.plotHeight]);
        }

        @Watch("options")
        onOptionsChanged(newOptions: ManhattanPlotOptions, oldOptions: ManhattanPlotOptions) {
            this.manhattanPlt.options(newOptions);
        }

        @Watch("dataPoints")
        onAssociationsChanged(newAssociations) {
            if(newAssociations.length>0){
                this.debouncedDrawManhattanPlot();
            }
        }

        @Watch('shown')
        onShownChanged(val, oldval) {
            if(val && !this.firstResize){
                this.onResize();
                this.firstResize = true;
            }
        }

        created() {
            const defaultOptions = {
                chr: 0,
                alpha: 0.05,
                max_y: 10,
                max_x: 100000,
                bonferroniThreshold: 10,
                permutationThreshold: 11,
            };
            // Add the missing parameters
            for (const key of Object.keys(defaultOptions)) {
                if (typeof this.options[key] === "undefined") {
                    this.options[key] = defaultOptions[key];
                }
            }
            this.manhattanPlt.options(this.options);
        }
        mounted() {
            d3.select("#komutationplot"+this.options.chr.toString()).data([this.dataPoints]).call(this.manhattanPlt);
            window.addEventListener('resize', this.debouncedOnResize);
            this.debouncedDrawManhattanPlot();
            this.debouncedOnResize();
        }

        beforeDestroy() {
            window.removeEventListener('resize', this.debouncedOnResize);
        }

        onResize() {
            this.width = this.$el.offsetWidth;
        }

        drawManhattanPlot() {
            this.manhattanPlt.clear();
            this.manhattanPlt.data(this.dataPoints);
        }


    }

</script>

<style>
    .manhattan {
        margin:25px;
        margin-bottom: 0;
    }

    #koassociationpopup{
        max-width:200px;
        position:absolute;
        z-index:9999;
    }

</style>
