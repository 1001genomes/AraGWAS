<template>
    <div ref="size">
        <svg id="chart" height="200" :width="width" ref="svg">
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
        width: number = 1000;
        scales = {x: d3.scaleLinear(), y: d3.scaleLinear()};
        readonly margin = {
            left: 40,
            right: 10,
            bottom: 40,
            top: 40,
        };
        scatterPlotHeight: number = 300;

        // TODO: add other options in props (currently only chr)
        // TODO: add hover functionality
        @Watch("$el.offsetWidth")
        reload() {
            this.onResize()
        }

        mounted() {
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
            // Add the missing parameters
            for (const key of Object.keys(defaultOptions)) {
                if (typeof this.options[key] === "undefined") {
                    this.options[key] = defaultOptions[key];
                }
            }
            this.onResize();
        }
        onResize() {
            this.width = this.$el.clientWidth;
            this.scales.x.range([this.margin.left, this.paddedScatter.width]);
            this.scales.y.range([this.paddedScatter.height, this.margin.top]);
            this.drawManhattan();
        }
        get paddedScatter() {
            const width = this.width - this.margin.left - this.margin.right;
            const height = this.scatterPlotHeight - this.margin.top - this.margin.bottom;
            return { width, height };
        }
        drawManhattan() {
            // define scaling options
            const options = this.options;
            const padding = 40;
            let w = this.width;
            const h = 185;

            this.scales.x.domain([0, options.max_x]);
            this.scales.x.range([padding, (w - padding)]);
            this.scales.y.domain([0, options.max_y + 1]);
            this.scales.y.range([h - padding, padding]);

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
                    .attr("x1", this.scales.x(valX * i))
                    .attr("y1", this.scales.y(0))
                    .attr("x2", this.scales.x(valX * i))
                    .attr("y2", this.scales.y(options.max_y + 1))
                    .style("stroke", "#CCC")
                    .style("stroke-width", 1);
                svg.append("svg:g")
                    .attr("transform", "translate(" + this.scales.x(valX * i) + "," + (h - padding / 1.5) + ")")
                    .append("text").text(valX * i)
                    .attr("text-anchor", "middle");
            }
            const valY = Math.round(options.max_y / 3);
            for (let i = 1; (i * valY) < (options.max_y + 1); i++) {
                svg.append("svg:line")
                    .attr("x1", this.scales.x(0))
                    .attr("y1", this.scales.y(valY * i))
                    .attr("x2", this.scales.x(options.max_x))
                    .attr("y2", this.scales.y(valY * i))
                    .style("stroke", "#CCC")
                    .style("stroke-width", 1);
                svg.append("svg:g")
                    .attr("transform", "translate(" + (padding / 1.5) + "," + this.scales.y(valY * i) + ")")
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
                .attr("x1", this.scales.x(0))
                .attr("y1", this.scales.y(options.max_y + 1))
                .attr("x2", this.scales.x(options.max_x))
                .attr("y2", this.scales.y(options.max_y + 1))
                .style("stroke", "#CCC")
                .style("stroke-width", 1.5 );
            svg.append("svg:line")
                .attr("x1", this.scales.x(options.max_x))
                .attr("y1", this.scales.y(0))
                .attr("x2", this.scales.x(options.max_x))
                .attr("y2", this.scales.y(options.max_y + 1))
                .style("stroke", "#CCC")
                .style("stroke-width", 1.5 );
            svg.append("svg:line")
                .attr("x1", this.scales.x(0))
                .attr("y1", this.scales.y(0))
                .attr("x2", this.scales.x(0))
                .attr("y2", this.scales.y(options.max_y + 1))
                .style("stroke", "#000000")
                .style("stroke-width", 1);
            svg.append("svg:line")
                .attr("x1", this.scales.x(0))
                .attr("y1", this.scales.y(0))
                .attr("x2", this.scales.x(options.max_x))
                .attr("y2", this.scales.y(0))
                .style("stroke", "#000000")
                .style("stroke-width", 1);
            svg.append("svg:g")
                .attr("transform", "translate(" + (padding * 4 + 25) + "," + (padding / 1.3) + ")")
                .append("text").text("Bonferroni threshold [" + options.alpha + "]");
            svg.append("svg:line")
                .attr("x1", this.scales.x(d2[0][0]))
                .attr("y1", this.scales.y(d2[0][1]))
                .attr("x2", this.scales.x(d2[1][0]))
                .attr("y2", this.scales.y(d2[1][1]))
                .style("stroke", "rgb(0,100,0)")
                .style("stroke-width", 1.5 );
            // draw datapoints
            svg.selectAll("circle")
                .data(this.dataPoints)
                .enter()
                .append("circle")
                .attr("cx", (d) => {
                    return this.scales.x(d[0]);
                })
                .attr("cy", (d) => {
                    return this.scales.y(d[1]);
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
