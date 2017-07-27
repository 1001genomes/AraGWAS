<template>
    <div>
        <svg id="heatmap" width="100%" :height="size[1]" >
        </svg>
    </div>
</template>

<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    import gwasheatmap from "../viz/gwasheatmap.js";

    import {loadAssociationsHeatmap} from "../api";

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
        async loadData() {
            this.data = await loadAssociationsHeatmap();
            // WORKAROUND create 4 additional copies
            let chrData = JSON.stringify(this.data["data"][0]);
            for (let i=2;i<6;i++) {
                let newChrData = JSON.parse(chrData);
                newChrData['chr'] = 'Chr'+ i;
                this.data['data'].push(newChrData);
            }
            d3.select("#heatmap").data([this.data]).call(this.heatmap);
        }

    }
</script>
<style lang="stylus">


</style>
