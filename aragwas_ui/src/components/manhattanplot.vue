<template>
    <div>
        <svg id="chart" height="250" width="100%" ref="svg" v-on:highlightsnp="onHighlightSnp">
        </svg>
        <div  v-bind:style="popupStyle" id="associationpopup"  >
            <v-card v-if="highlightedAssociation != null" >
                <v-card-title class="green darken-1" >
                    <h3 class="headline mb-0 white--text">{{highlightedAssociation.name}}</h3>
                </v-card-title>
                <v-card-text>
                    <dl>
                        <dt>Position:</dt><dd>{{highlightedAssociation.originalStart}}</dd>
                        <dt>SCore:</dt><dd>{{highlightedAssociation.description}}</dd>
                    </dl>
                </v-card-text>
                <v-card-title class="green darken-1">
                    <span class="white--text"></span>
                    <v-spacer></v-spacer>
                </v-card-title>
            </v-card>
        </div>
    </div>
</template>
<script lang="ts">
    import * as d3 from "d3";
    import Vue from "vue";
    import {Component, Prop, Watch} from "vue-property-decorator";
    import _ from "lodash";

    @Component({
        name: "manhattan-plot",
        props: ["dataPoints", "options", "shown"],
    })
    export default class ManhattanPlot extends Vue {
        @Prop()
        dataPoints;
        @Prop()
        options;
        @Prop()
        shown;

        width: number = 1000;
        firstResize = false;
        scales = {x: d3.scaleLinear(), y: d3.scaleLinear()};
        readonly margin = {
            left: 40,
            right: 10,
            bottom: 40,
            top: 40,
        };
        readonly padding = 40;
        readonly h = 235;
        debouncedResize = _.debounce(this.onResize, 200);
        highlightedAssociation: Object | null = null;
        popupStyle = {
            top: '0',
            left: '0'
        }


        get blue() {
            return 204 - (this.options.color) * 40;
        }
        get red() {
            return 51 + (this.options.color) * 40;
        }
        get paddedScatter() {
            const width = this.width - this.margin.left - this.margin.right;
            const height = this.h - this.padding;
            return { width, height };
        }

        @Watch('dataPoints')
        onDataPointsChanged(val, oldval) {
            this.drawPoints();
            this.drawBonferroni();
        }
        @Watch('shown')
        onShownChanged(val, oldval) {
            if(val && !this.firstResize){
                this.onResize();
                this.firstResize = true;
            }
        }

        // TODO: add hover functionality
        mounted() {
            window.addEventListener('resize', this.debouncedResize);
            // Width and height
            let w = this.options.width;
            if (typeof w === "undefined") {
                w = 1200;
            }
            const defaultOptions = {
                chr: 0,
                alpha: 0.05,
                max_y: 10,
                max_x: 100000,
                bonferroniThreshold: 10,
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
            const options = this.options;
            // define scaling options
            this.scales.x.domain([0, options.max_x]);
            this.scales.x.range([this.padding, (w - this.padding)]);
            this.scales.y.domain([0, options.max_y + 1]);
            this.scales.y.range([this.h - this.padding, this.padding]);
            // draw svg
            this.draw();
            this.drawPoints()

        }
        beforeDestroy() {
            window.removeEventListener('resize', this.debouncedResize);
        }
        onHighlightSnp(d) {
            this.highlightedAssociation = {name: "Chr"+this.options.chr.toString()+":"+d[0].toString(), position: d[0].toString(), score: d[1].toString()}
        }
        onResize() {
            this.width = this.$el.offsetWidth;
            this.scales.x.range([this.margin.left, this.paddedScatter.width]);
            this.scales.y.domain([0, this.options.max_y + 1]);
            this.scales.y.range([this.paddedScatter.height, this.margin.top]);
            const svg = d3.select(this.$refs.svg as Element);
            svg.selectAll("g").remove();
            svg.selectAll("line").remove();
            svg.selectAll("circle").remove();
            this.draw();
            this.drawPoints();
            this.drawBonferroni();
        }
        draw() {
            // draw svg
            const options = this.options;
            const h = this.h;
            let w = this.$el.offsetWidth;
            const svg = d3.select(this.$refs.svg as Element);
            const len = Math.pow(10, ((String(Math.round(options.max_x / 5)).length - 1)));
            const valX = Math.round(options.max_x / 5 / len) * len;
            // draw graph help-lines in background
            for (let i = 0; (valX * i) < options.max_x ; i++) {
                svg.append("svg:g")
                    .attr("transform", "translate(" + this.scales.x(valX * i) + "," + (h - this.padding / 1.5) + ")")
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
                    .attr("transform", "translate(" + (this.padding / 1.5) + "," + this.scales.y(valY * i) + ")")
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
                .attr("transform", "translate(" + ((this.padding - 0.85*h)) + "," + (this.padding / 3) + ")")
                .append("text").text("-log10(p-value)");
            svg.append("svg:line")
                .attr("x1", this.scales.x(0))
                .attr("y1", this.scales.y(0))
                .attr("x2", this.scales.x(options.max_x))
                .attr("y2", this.scales.y(0))
                .style("stroke", "#000000")
                .style("stroke-width", 1);
            svg.append("svg:g")
                .attr("transform", "translate(" + ((w - this.padding) / 2) + "," + (h - this.padding / 5) + ")")
                .append("text").text("chromosomal position [bp]")
                .attr("text-anchor", "middle");
            svg.append("rect")
                .attr("x", this.padding)
                .attr("y", this.padding / 1.6)
                .attr("width", this.padding / 2.5)
                .attr("height", this.padding / 3.5)
                .style("fill", "rgb(" + this.red + ",102," + this.blue + ")");
            svg.append("svg:g")
                .attr("transform", "translate(" + (this.padding + 25) + "," + (this.padding / 1.1) + ")")
                .append("text").text("-log10(p-value)");
            svg.append("rect")
                .attr("x", this.padding * 4 + 25)
                .attr("y", this.padding / 1.6)
                .attr("width", this.padding / 2.5)
                .attr("height", this.padding / 3.5)
                .style("fill", "rgb(0,100,0)");
            svg.append("svg:g")
                .attr("transform", "translate(" + (this.padding * 4 + 50) + "," + (this.padding / 1.1) + ")")
                .append("text").text("Bonferroni threshold [" + options.alpha + "]");
        }
        drawPoints() {
            const div = d3.select(this.$refs.svg as Element)
                .append("div")  // declare the tooltip div
                .attr("class", "tooltip")              // apply the 'tooltip' class
                .style("opacity", 0);                  // set the opacity to nil
            const svg = d3.select(this.$refs.svg as Element);
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
                .attr("r", 2.5)
                .on("mouseover", function(d) {
//                    console.log(div);
                    d3.select(this).attr("r",6);
//                    svg.dispatch("highlightsnp", { detail: {snp: d, event: d3.event}});
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
                    div.transition()
                        .duration(200)
                        .style("opacity", .9);
                    div.html('<v-card href= "http://google.com"> ASS</v-card>')
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 45) + "px");
                })
                .on("mouseout", function(d,i) {
                    d3.select(this).attr("r",2.5)
                })
                .style("fill", "rgb(" + this.red + ",102," + this.blue + ")");
        }
        drawBonferroni() {
            const d2 = [[0, this.options.bonferroniThreshold], [this.options.max_x, this.options.bonferroniThreshold]];
            const svg = d3.select(this.$refs.svg as Element);
            svg.append("svg:line")
                .attr("x1", this.scales.x(d2[0][0]))
                .attr("y1", this.scales.y(d2[0][1]))
                .attr("x2", this.scales.x(d2[1][0]))
                .attr("y2", this.scales.y(d2[1][1]))
                .style("stroke", "rgb(0,100,0)")
                .style("stroke-width", 1.5 );
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
    div.tooltip {
        position: absolute;
        text-align: center;
        width: 60px;
        height: 40px;
        padding: 2px;
        font: 12px sans-serif;
        background: forestgreen;
        border: 0;
        border-radius: 8px;
    }
    #associationpopup {
        max-width: 400px;
        position: absolute;
        z-index: 9999;
    }
</style>
