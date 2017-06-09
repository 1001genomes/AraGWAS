<template>
    <div>
        <svg id="chart" height="200" width="100%" ref="svg">
        </svg>
    </div>
</template>
<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";

    @Component({
        name: "manhattan-plot",
        props: ["dataPoints", "options"],
    })
    export default class ManhattanPlot extends Vue {
        @Prop()
        dataPoints;
        @Prop()
        options;
        // TODO: add other options in props (currently only chr)
        // TODO: auto adjustment of window size
        // TODO: add hover functionality
        mounted() {
            // Width and height
            const padding = 40;
            let w = this.options.width;
            if (typeof w === "undefined") {
                w = 1200;
            }
            const h = 185;
            const scaleW = d3.scaleLinear();
            const scaleH = d3.scaleLinear();

            const defaultOptions = {
                matrix: undefined,
                species_id: undefined,
                chr: 0,
                alpha: 0.05,
                max_y: 10,
                max_x: 100000,
                bonferoniThreshold: 10,
                div: undefined,
                divLegend: undefined,
                xlabel: "x",
                ylabel: "y",
                legend1: "",
                legend2: "",
                color: this.options.chr,
                limited: 0,
            };
            const options = this.options;
            // Add the missing parameters
            for (const key of Object.keys(defaultOptions)) {
                if (typeof options[key] === "undefined") {
                    options[key] = defaultOptions[key];
                }
            }

            // define scaling options
            scaleW.domain([0, options.max_x]);
            scaleW.range([padding, (w - padding)]);
            scaleH.domain([0, options.max_y + 1]);
            scaleH.range([h - padding, padding]);

            // define colors
            const blue = 204 - (options.color) * 40;
            const red = 51 + (options.color) * 40;
            // get data
            const data = options.matrix;
            const d2 = [[0, options.bonferoniThreshold], [options.max_x, options.bonferoniThreshold]];
            // draw svg
            const svg = d3.select(this.$refs.svg as Element)
                .append("svg")
                .attr("width", w)
                .attr("height", h);
            const len = Math.pow(10, ((String(Math.round(options.max_x / 5)).length - 1)));
            const valX = Math.round(options.max_x / 5 / len) * len;
            // draw graph help-lines in background
            for (let i = 0; (valX * i) < options.max_x ; i++) {
                svg.append("svg:line")
                    .attr("x1", scaleW(valX * i))
                    .attr("y1", scaleH(0))
                    .attr("x2", scaleW(valX * i))
                    .attr("y2", scaleH(options.max_y + 1))
                    .style("stroke", "#CCC")
                    .style("stroke-width", 1);
                svg.append("svg:g")
                    .attr("transform", "translate(" + scaleW(valX * i) + "," + (h - padding / 1.5) + ")")
                    .append("text").text(valX * i)
                    .attr("text-anchor", "middle");
            }
            const valY = Math.round(options.max_y / 3);
            for (let i = 1; (i * valY) < (options.max_y + 1); i++) {
                svg.append("svg:line")
                    .attr("x1", scaleW(0))
                    .attr("y1", scaleH(valY * i))
                    .attr("x2", scaleW(options.max_x))
                    .attr("y2", scaleH(valY * i))
                    .style("stroke", "#CCC")
                    .style("stroke-width", 1);
                svg.append("svg:g")
                    .attr("transform", "translate(" + (padding / 1.5) + "," + scaleH(valY * i) + ")")
                    .append("text").text(valY * i)
                    .attr("text-anchor", "middle");
            }
            // write text-information to axis and draw graph-elements
            svg.append("svg:g")
                .attr("transform", "translate(" + 5 + "," + 12 + ")")
                .append("text").text("Manhattan-plot for chromosome " + options.chr)
                .style("font-weight", "bold");
            svg.append("svg:g")
                .attr("transform", "matrix(0, -1, 1, 0, 0, 0)").append("svg:g")
                .attr("transform", "translate(" + ((padding - h)) + "," + (padding / 3) + ")")
                .append("text").text("-log10(p-value)");
            svg.append("svg:g")
                .attr("transform", "translate(" + ((w - padding) / 2) + "," + (h - padding / 5) + ")")
                .append("text").text("chromosomal position [bp]")
                .attr("text-anchor", "middle");
            svg.append("rect")
                .attr("x", padding)
                .attr("y", padding / 2)
                .attr("width", padding / 2.5)
                .attr("height", padding / 3.5)
                .style("fill", "rgb(" + red + ",102," + blue + ")");
            svg.append("svg:g")
                .attr("transform", "translate(" + (padding + 25) + "," + (padding / 1.3) + ")")
                .append("text").text("-log10(p-value)");
            svg.append("rect")
                .attr("x", padding * 4)
                .attr("y", padding / 2)
                .attr("width", padding / 2.5)
                .attr("height", padding / 3.5)
                .style("fill", "rgb(0,100,0)");
            svg.append("svg:line")
                .attr("x1", scaleW(0))
                .attr("y1", scaleH(options.max_y + 1))
                .attr("x2", scaleW(options.max_x))
                .attr("y2", scaleH(options.max_y + 1))
                .style("stroke", "#CCC")
                .style("stroke-width", 1.5 );
            svg.append("svg:line")
                .attr("x1", scaleW(options.max_x))
                .attr("y1", scaleH(0))
                .attr("x2", scaleW(options.max_x))
                .attr("y2", scaleH(options.max_y + 1))
                .style("stroke", "#CCC")
                .style("stroke-width", 1.5 );
            svg.append("svg:line")
                .attr("x1", scaleW(0))
                .attr("y1", scaleH(0))
                .attr("x2", scaleW(0))
                .attr("y2", scaleH(options.max_y + 1))
                .style("stroke", "#000000")
                .style("stroke-width", 1);
            svg.append("svg:line")
                .attr("x1", scaleW(0))
                .attr("y1", scaleH(0))
                .attr("x2", scaleW(options.max_x))
                .attr("y2", scaleH(0))
                .style("stroke", "#000000")
                .style("stroke-width", 1);
            svg.append("svg:g")
                .attr("transform", "translate(" + (padding * 4 + 25) + "," + (padding / 1.3) + ")")
                .append("text").text("Bonferroni threshold [" + options.alpha + "]");
            svg.append("svg:line")
                .attr("x1", scaleW(d2[0][0]))
                .attr("y1", scaleH(d2[0][1]))
                .attr("x2", scaleW(d2[1][0]))
                .attr("y2", scaleH(d2[1][1]))
                .style("stroke", "rgb(0,100,0)")
                .style("stroke-width", 1.5 );
            // draw datapoints
            svg.selectAll("circle")
                .data(this.dataPoints)
                .enter()
                .append("circle")
                .attr("cx", (d) => {
                    return scaleW(d[0]);
                })
                .attr("cy", (d) => {
                    return scaleH(d[1]);
                })
                .attr("r", 2.1)
                .style("fill", "rgb(" + red + ",102," + blue + ")");
        }
    }
</script>
<style >
    #chart {
        margin:25px;
    }
    #chart path {
        fill: transparent;
        stroke: green;
    }
</style>
