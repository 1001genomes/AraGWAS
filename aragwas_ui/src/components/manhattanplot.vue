<template>
    <div>
        <svg id="chart" height="200" width="2000" ref="svg">
        </svg>
    </div>
</template>

<script lang="ts">
    import {Component, Prop, Watch} from 'vue-property-decorator';
    import * as d3 from 'd3';
    import Vue from 'vue';

    @Component({
        name: 'manhattan-plot',
    })
    export default class ManhattanPlot extends Vue {
        data = [[3021, 10], [1231, 2]]

        mounted() {
            //Width and height
            var padding = 40;
            var w = 1200;
            var h = 185;
            var scaleW = d3.scaleLinear();
            var scaleH = d3.scaleLinear();
            var options = {
                matrix: undefined,
                species_id: undefined,
                chr: 0,
                alpha: 0.05,
                max_y: 10,
                max_x: 10000,
                bonferoniThreshold: 10,
                div: undefined,
                divLegend: undefined,
                xlabel: "x",
                ylabel: "y",
                legend1: "",
                legend2: "",
                color:0,
                limited:0,
            };

            // define scaling options
            scaleW.domain([0, options.max_x]);
            scaleW.range([padding, (w-padding)]);
            scaleH.domain([0, options.max_y+1]);
            scaleH.range([h-padding, padding]);

            // define colors
            var blue = 204 - (options.color) * 40;
            var red = 51 + (options.color) * 40;
            // get data
            var data = options.matrix;
            var d2 = [[0,options.bonferoniThreshold],[options.max_x,options.bonferoniThreshold]];
            // draw svg
            var svg = d3.select(this.$refs.svg as Element)
                .append("svg")
                .attr("width", w)
                .attr("height", h);
            var len = Math.pow(10,((String(Math.round(options.max_x/5)).length-1)));
            var val_x = Math.round(options.max_x/5/len)*len;
            // draw graph help-lines in background
            for (var i = 0; (val_x*i) < options.max_x ; i++) {
                svg.append("svg:line")
                    .attr("x1", scaleW(val_x*i))
                    .attr("y1", scaleH(0))
                    .attr("x2", scaleW(val_x*i))
                    .attr("y2", scaleH(options.max_y+1))
                    .style("stroke", "#CCC")
                    .style("stroke-width",1);
                svg.append("svg:g")
                    .attr("transform", "translate("+scaleW(val_x*i)+","+(h-padding/1.5)+")")
                    .append("text").text(val_x*i)
                    .attr("text-anchor", "middle");
            };
            var val_y = Math.round(options.max_y/3)
            for (var i = 1; (i*val_y) < (options.max_y+1); i++) {
                svg.append("svg:line")
                    .attr("x1", scaleW(0))
                    .attr("y1", scaleH(val_y*i))
                    .attr("x2", scaleW(options.max_x))
                    .attr("y2", scaleH(val_y*i))
                    .style("stroke", "#CCC")
                    .style("stroke-width",1);
                svg.append("svg:g")
                    .attr("transform", "translate("+(padding/1.5)+","+scaleH(val_y*i)+")")
                    .append("text").text(val_y*i)
                    .attr("text-anchor", "middle");
            };
            // write text-information to axis and draw graph-elements
            svg.append("svg:g")
                .attr("transform", "translate("+5+","+12+")")
                .append("text").text("Manhattan-plot for chromosome "+options.chr)
                .style("font-weight","bold")
            svg.append("svg:g")
                .attr("transform", "matrix(0, -1, 1, 0, 0, 0)").append("svg:g")
                .attr("transform", "translate("+((padding-h))+","+(padding/3)+")")
                .append("text").text("-log10(p-value)");
            svg.append("svg:g")
                .attr("transform", "translate("+((w-padding)/2)+","+(h-padding/5)+")")
                .append("text").text("chromosomal position [bp]")
                .attr("text-anchor", "middle");
            svg.append("rect")
                .attr("x", padding)
                .attr("y", padding/2)
                .attr("width", padding/2.5)
                .attr("height", padding/3.5)
                .style("fill", "rgb("+red+",102,"+blue+")");
            svg.append("svg:g")
                .attr("transform", "translate("+(padding+25)+","+(padding/1.3)+")")
                .append("text").text("-log10(p-value)");
            svg.append("rect")
                .attr("x", padding*4)
                .attr("y", padding/2)
                .attr("width", padding/2.5)
                .attr("height", padding/3.5)
                .style("fill", "rgb(0,100,0)");
            svg.append("svg:line")
                .attr("x1", scaleW(0))
                .attr("y1", scaleH(options.max_y+1))
                .attr("x2", scaleW(options.max_x))
                .attr("y2", scaleH(options.max_y+1))
                .style("stroke", "#CCC")
                .style("stroke-width",1.5 );
            svg.append("svg:line")
                .attr("x1", scaleW(options.max_x))
                .attr("y1", scaleH(0))
                .attr("x2", scaleW(options.max_x))
                .attr("y2", scaleH(options.max_y+1))
                .style("stroke", "#CCC")
                .style("stroke-width",1.5 );
            svg.append("svg:line")
                .attr("x1", scaleW(0))
                .attr("y1", scaleH(0))
                .attr("x2", scaleW(0))
                .attr("y2", scaleH(options.max_y+1))
                .style("stroke", "#000000")
                .style("stroke-width",1);
            svg.append("svg:line")
                .attr("x1", scaleW(0))
                .attr("y1", scaleH(0))
                .attr("x2", scaleW(options.max_x))
                .attr("y2", scaleH(0))
                .style("stroke", "#000000")
                .style("stroke-width",1);
            svg.append("svg:g")
                .attr("transform", "translate("+(padding*4+25)+","+(padding/1.3)+")")
                .append("text").text("Bonferroni threshold ["+options.alpha+"]");
            svg.append("svg:line")
                .attr("x1", scaleW(d2[0][0]))
                .attr("y1", scaleH(d2[0][1]))
                .attr("x2", scaleW(d2[1][0]))
                .attr("y2", scaleH(d2[1][1]))
                .style("stroke", "rgb(0,100,0)")
                .style("stroke-width",1.5 );
            // draw datapoints
            svg.selectAll("circle")
                .data(this.data)
                .enter()
                .append("circle")
                .attr("cx", function(d) {
                    return scaleW(d[0]);
                })
                .attr("cy", function(d) {
                    return scaleH(d[1]);
                })
                .attr("r", 2.1)
                .style("fill", "rgb("+red+",102,"+blue+")")
        };

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