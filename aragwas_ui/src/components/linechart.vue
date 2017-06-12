<template>
    <div>
        <svg id="chart" height="100%" width="100%" ref="svg">
        </svg>
    </div>
</template>

<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    interface ChartData {
        readonly x: number;
        readonly y: number;
    }

    @Component({
        name: "line-chart",
        props: ["width"],
    })
    export default class LineChart extends Vue {
        values: ChartData[] = [ { x: 0, y: 30 }, { x: 50, y: 20 }, { x: 100, y: 40 }, { x: 150, y: 80 }, { x: 200, y: 95 }];
        @Prop()
        width;

        mounted() {

            const svg = d3.select(this.$refs.svg as Element);
            let xMax = d3.max(this.values, (d) => d.x);
            if (!xMax) {
                xMax = Number.MAX_VALUE;
            }
            let yMax = d3.max(this.values, (d) => d.y);
            if (!yMax) {
                yMax = Number.MAX_VALUE;
            }

            const x = d3.scaleLinear().range([0, 600]).domain([0, xMax]);
            const y = d3.scaleLinear().range([200, 0]).domain([0, yMax]);
            const axis = d3.axisLeft(x);

            const line: any = d3.line<ChartData>()
                .x((d) => x(d.x))
                .y((d) => y(d.y));
            svg.append("g").attr("transform", "translate(25,25)").call(axis).append("path").attr("stroke-width", 2).attr("d", line(this.values));
        }
    }
</script>
<style scoped>
    #chart {
        margin:25px;
    }
    #chart path {
        fill: transparent;
        stroke: green;
    }
</style>
