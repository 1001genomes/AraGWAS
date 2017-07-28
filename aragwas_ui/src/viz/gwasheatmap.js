import * as d3 from "d3";
import {schemeYlOrRd, interpolateYlOrRd} from "d3-scale-chromatic";
import _ from "lodash";

export default function gwasHeatmap() {
    var svg;
    var size = [800, 1000];
    var data;
    var scoreRange;
    var minScoreToDisplay = 0;
    var orientation = "horizontal";
    var xScale = d3.local();
    var histogramScale = d3.local();

    var yScale;
    var padding = 50;
    var margin = { "top": 10, "bottom": 50, "left": 100, "right": 50 };
    var transitionDuration = 150;
    var colorScale = d3.scaleQuantile();
    var fillScale = d3.scaleLinear().clamp(true);
    var histogramHeight = 100;
    var cellSize = 12;
    var legendElementWidth = cellSize * 2.5;
    var legendHeight = 50;

    var draw, ticks;

    function getScatterPlotTop() {
        return histogramHeight + margin.top;
    }

    function getPlotWidth() {
        return size[0] - margin.left - margin.right;
    }

    function getChromosomeWidth() {
        return getPlotWidth() / data.data.length;
    }

    function getPlotHeight() {
        return size[1] - margin.bottom - margin.top - histogramHeight - legendHeight;
    }

    function getDataPointSize(d) {
        return 2;
    }

    function ticks() {
        return Math.floor(getChromosomeWidth() / 40);
    }

    function initData() {
        scoreRange = data.scoreRange;
        //var midPoint = scoreRange[1] - scoreRange[0] / 2;
        let values = _.flatten(_.flatten(data.data.map(d => d.data) )).map(d => d.score);
        colorScale.domain(values).range(schemeYlOrRd[9]);
        fillScale.domain(scoreRange);
        if (data.type === "top") {
            yScale = d3.scalePoint().domain(data.studies.map(function(d) { return d.name; }));
        }
    }

    function mouseover(p, ix) {
        var studyIdx = parseInt(this.parentNode.dataset.index);
        d3.selectAll(".y.axis text").filter(function(d, i) { return i === studyIdx; }).style("fill", "red");
        d3.select(this).attr("r", function(d) { return getDataPointSize() * 1.5; });
    }

    function mouseout(p, ix) {
        d3.selectAll("text").classed("active", false);
        var studyIdx = parseInt(this.parentNode.dataset.index);
        d3.selectAll(".y.axis text").filter(function(d, i) { return i === studyIdx; }).style("fill", "#000");
        d3.select(this).attr("r", getDataPointSize);
    }

    function chart(selection) {

        function drawCell(row) {
            var cell = d3.select(this).selectAll(".cell")
                .data(row, function(d) { return d.pos; })
                .enter().append("circle")
                .attr("class", "cell")
                .attr("cx", function(d) { return xScale.get(this)(d.pos); })
                .attr("cy", function(d, i) { return yScale(i); })
                .attr("r", getDataPointSize)
                //.style("fill-opacity", function(d) { return fillScale(d.score); })
                .style("fill", function(d) { return colorScale(d.score); })
                .on("mouseover", mouseover)
                .on("mouseout", mouseout);
        }

        draw = function() {
            svg.selectAll("g.chr")
                .attr("transform", function(d, i) {
                    return "translate(" + (margin.left + i * getChromosomeWidth()) + ",0)";
                })
                .each(function(d) {
                    var range = [0, getChromosomeWidth() - padding];
                    var histogram = histogramScale.get(this);
                    histogram.x.domain(d.bins.map(function(b, ix) { return ix; })).range(range);
                    histogram.y.domain(d3.extent(d.bins)).range([histogramHeight, 0]);
                    xScale.get(this).domain(d.region).range(range);
            });

            drawAxes();
            drawPoints();
            drawHistograms();
            drawLegend();
        };

        function drawLegend() {
            var legend = svg.selectAll(".legend")
                .attr("transform", "translate(" + getPlotWidth() / 2  + "," + (size[1] - margin.bottom / 2) + ")")
                .selectAll(".legendItem")
                .data(schemeYlOrRd[9])
                .enter().append("g")
                .attr("class", "legendItem");

            legend.append("rect")
                .attr("x", function(d, i) { return legendElementWidth * i; })
                .attr("y", 0)
                .attr("width", legendElementWidth)
                .attr("height", cellSize)
                .style("fill", function(d, i) { return d; });

            legend.append("text")
                .text(function(d) {
                    var extend  = colorScale.invertExtent(d);
                    return Math.round(extend[0]);
                 })
                .attr("x", function(d, i) { return legendElementWidth * i; })
                .attr("y", (cellSize * 2))
                .style("font-size", 10);

        }

        function drawHistograms() {
            var bars = svg.selectAll("g.chr")
                .selectAll("g.histogram").selectAll("rect.bar").data(function(d) { return d.bins; });
            bars.enter()
                .append("rect")
                .style("fill", "steelblue")
                .attr("x", function(d, i) { return histogramScale.get(this).x(i); })
                .attr("width", function(d) { return histogramScale.get(this).x.bandwidth(); })
                .attr("y", function(d) { return histogramScale.get(this).y(d); })
                .attr("height", function(d) { return histogramHeight - histogramScale.get(this).y(d); });
        }

        function drawPoints() {
            var row = svg.selectAll("g.chr").selectAll("g.scatterplot")
                .selectAll("g.row")
                .data(function(d, i) { return d.data; }, function(d) { return d.pos; });

            row.exit().remove();
            row.enter().append("g")
                .attr("class", "row")
                .attr("data-index", function(d, ix) { return ix; })
                .attr("transform", function(d, i) { return "translate(0," + yScale(data.studies[i].name) + ")"; })
                .each(drawCell);getPlotWidth
        }

        function drawAxes() {

            yScale.range([0, getPlotHeight()]);
            svg.selectAll("g.x.axis")
                .attr("transform", function(d) {
                    return "translate(0," + (getPlotHeight() + getScatterPlotTop() + margin.top) + ")";
                })
                .transition().duration(transitionDuration)
                .each(function(d) {
                    d3.axisBottom(xScale.get(this)).ticks(ticks()).tickFormat(d3.formatPrefix(".1", 1e6))(d3.select(this));
                });

            svg.selectAll(".xaxislabel")
                .attr("x", getChromosomeWidth() / 2 - 71)
                .attr("y", (getPlotHeight() + getScatterPlotTop() + margin.top + margin.bottom  ));


            svg.select("g.y.axis")
                .transition().duration(transitionDuration)
                .call(d3.axisLeft(yScale));
        }

        selection.each(function(dt) {
            svg = d3.select(this);
            data = dt;
            initData();

            svg.append("g")
                .attr("class", "y axis")
                .attr("transform", "translate(" + margin.left + "," + getScatterPlotTop() + ")")
                .call(d3.axisLeft(yScale));

            svg.append("g")
                .attr("class", "legend");

            var chromGroups = svg.selectAll("g.chr")
                .data(data.data, function(d) { return d.chr; });

            chromGroups.exit().remove();

            var chromGroupsEntered = chromGroups.enter()
                .append("g")
                .attr("class", "chr")
                .attr("id", function(d) { return d.chr; })
                .each(function(d) {
                    histogramScale.set(this, { x: d3.scaleBand(), y: d3.scaleLinear() });
                    xScale.set(this, d3.scaleLinear());
                });

            chromGroupsEntered
                .append("g")
                .attr("class", "x axis")
                .call(function(d) { d3.axisBottom(xScale.get(d.node()))(d); });

            chromGroupsEntered
                .append("text")
                .attr("class", "xaxislabel")
                .text(function(d) { return d.chr + " (Mbp)";});


            chromGroupsEntered
                .append("g")
                .attr("class", "scatterplot")
                .attr("transform", "translate(0, " + getScatterPlotTop() + ")");

            chromGroupsEntered
                .append("g")
                .attr("class", "histogram");

            chromGroups = chromGroupsEntered.merge(chromGroups);

            draw();
        });
    }

    chart.size = function(value) {
        if (!arguments.length) {
            return size;
        }
        size = value;
        if (typeof draw === "function") {
            draw();
        }
    };

    return chart;
}
