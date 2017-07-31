<template>
    <div>
        <h3 v-if="!loaded" class="mt-4 mb-4 text-xs-center">The loading can take some time (~20s). Thank you for your patience.</h3>
        <v-progress-linear v-bind:indeterminate="true" v-if="!loaded" ></v-progress-linear>
        <svg id="heatmap" width="100%" :height="size[1]" >
        </svg>
    </div>
</template>

<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import gwasheatmap from "../viz/gwasheatmap.js";

    import {loadAssociationsHeatmap, loadAssociationsHistogram} from "../api";

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

        mounted() {
            this.loadData();
            window.addEventListener('resize', this.debouncedOnResize);
            this.debouncedOnResize();
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
            return Math.round(30427671 / ((this.width  - 150) / 5));
        }

        @Watch("size")
        onWidthChanged(newSize: number[], oldSize: number[]) {
            this.heatmap.size(newSize);
        }

        onResize() {
            this.width = this.$el.offsetWidth;
            if (this.$el.parentElement) {
                this.height = this.$el.parentElement.offsetHeight;
            }
        }
        loadData() {
            this.loaded=false;
            Promise.all([loadAssociationsHeatmap(), loadAssociationsHistogram(this.regionWidth)])
                .then((results) => {
                    let data = results[0];
                    let histogramData = results[1];
                    for (let i=0;i<histogramData['data'].length;i++) {
                        data['data'][i]['bins'] = histogramData['data'][i]['bins'];
                    }
                    this.data = data;
                    this.loaded=true;
                    d3.select("#heatmap").data([this.data]).call(this.heatmap);
                });
        }

    }
</script>
<style lang="stylus">


</style>
